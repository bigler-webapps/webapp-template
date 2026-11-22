// The app identity comes from test-management.consumer.json; nothing here needs renaming.
// Only the container receives the controller credential; JSON travels on stdin.
import { spawn, spawnSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';

const MAX_BYTES = 1024 * 1024;

function consumerIdentity(root) {
  try {
    return JSON.parse(readFileSync(path.join(root, 'test-management.consumer.json'), 'utf8')).identity;
  } catch {
    return undefined;
  }
}

export class ControllerBridge {
  constructor(project) {
    const handle = /^([a-z][a-z0-9]*(?:-[a-z0-9]+)*)-tm-[a-f0-9]{32}$/.exec(project || '');
    if (!handle) {
      throw new Error('Invalid isolated instance handle');
    }
    const identity = handle[1];
    let host = process.env.DOCKER_HOST;
    if (!host) {
      const context = spawnSync('docker', ['context', 'inspect', '--format', '{{.Endpoints.docker.Host}}'], {
        stdio: ['ignore', 'pipe', 'ignore'], encoding: 'utf8', timeout: 15000, windowsHide: true,
      });
      if (context.status !== 0) throw new Error('Local Docker context unavailable');
      host = context.stdout.trim();
    }
    if (!(host.startsWith('unix:///') || host.toLowerCase().startsWith('npipe:////./pipe/'))) {
      throw new Error('Controller requires a local Docker daemon');
    }
    this.dockerHost = host;
    this.project = project;
    // The central acceptance runner starts in .claude/acceptance; Playwright
    // starts in frontend. Both resolve to the same explicit repository root.
    const roots = [...new Set([
      path.resolve(process.cwd(), '..'),
      path.resolve(process.cwd(), '../..', identity),
      path.resolve(process.cwd()),
    ])].filter((root) => existsSync(path.join(root, 'docker-compose.test-management.yml')) &&
      existsSync(path.join(root, 'frontend', 'tests', 'test-management-controller.js')) &&
      consumerIdentity(root) === identity);
    if (roots.length !== 1) throw new Error('Isolated controller repository is ambiguous or unavailable');
    this.cwd = roots[0];
  }

  async request(method, path, body) {
    const input = JSON.stringify({ method, path, ...(body === undefined ? {} : { body }) });
    if (Buffer.byteLength(input) > MAX_BYTES) throw new Error('Controller request too large');
    return new Promise((resolve, reject) => {
      const composeEnv = { ...process.env, TEST_MANAGEMENT_IMAGE: 'bridge-placeholder:local', TEST_MANAGEMENT_DATABASE: 'bridge_placeholder', TEST_MANAGEMENT_DATABASE_PASSWORD: 'bridge_placeholder',
        TEST_MANAGEMENT_DJANGO_SECRET: 'bridge_placeholder', TEST_MANAGEMENT_INSTANCE_ID: '00000000-0000-0000-0000-000000000000',
        TEST_MANAGEMENT_CONTROLLER_TOKEN: 'bridge_placeholder', TEST_MANAGEMENT_SUBNET: '10.0.0.0/24' };
      delete composeEnv.ENV_TYPE;
      delete composeEnv.DOCKER_CONTEXT;
      composeEnv.DOCKER_HOST = this.dockerHost;
      const child = spawn('docker', ['compose', '-p', this.project, '-f', 'docker-compose.test-management.yml', 'exec', '-T', 'backend', 'python', '-m', 'django_core_micha.test_management.local_bridge'], {
        cwd: this.cwd,
        env: composeEnv,
        stdio: ['pipe', 'pipe', 'ignore'], windowsHide: true,
      });
      let output = '';
      const timeout = setTimeout(() => child.kill(), 30000);
      child.stdout.setEncoding('utf8');
      child.stdout.on('data', (chunk) => {
        output += chunk;
        if (Buffer.byteLength(output) > MAX_BYTES) child.kill();
      });
      child.on('error', () => { clearTimeout(timeout); reject(new Error('Local controller unavailable')); });
      child.on('close', (code) => {
        clearTimeout(timeout);
        if (code !== 0 || Buffer.byteLength(output) > MAX_BYTES) return reject(new Error('Local controller unavailable'));
        try {
          const result = JSON.parse(output);
          if (!Number.isInteger(result.status)) throw new Error('invalid');
          resolve({ status: () => result.status, ok: () => result.status >= 200 && result.status < 300, json: async () => result.body });
        } catch {
          reject(new Error('Invalid controller response'));
        }
      });
      child.stdin.on('error', () => {});
      child.stdin.end(input);
    });
  }

  get(path) { return this.request('GET', path); }
  post(path, options = {}) { return this.request('POST', path, options.data); }
  patch(path, options = {}) { return this.request('PATCH', path, options.data); }
  delete(path) { return this.request('DELETE', path); }
  async dispose() {}
}

