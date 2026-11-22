// Controller authority stays in the isolated container; browser state stays in memory.
import { randomUUID } from 'node:crypto';
import { ControllerBridge } from './test-management-controller.js';

export class TestManagementClient {
  constructor(project, baseURL, browser) {
    const origin = new URL(baseURL);
    if (origin.protocol !== 'http:' || !['127.0.0.1', '[::1]'].includes(origin.hostname) ||
        origin.username || origin.password || !['', '/'].includes(origin.pathname) || origin.search || origin.hash) {
      throw new Error('A loopback HTTP origin is required');
    }
    this.baseURL = origin.origin;
    this.browser = browser;
    this.controller = new ControllerBridge(project);
    this.sessions = new Map();
  }

  async request(method, path, body) {
    const response = await this.controller.request(method, path, body);
    const result = await response.json();
    if (!response.ok()) {
      const error = new Error('Test management request failed');
      error.status = response.status();
      error.code = typeof result?.code === 'string' ? result.code : 'request_failed';
      throw error;
    }
    return result;
  }

  discovery() { return this.request('GET', '/api/test-management/discovery/'); }
  createRun(body) { return this.request('POST', '/api/test-management/runs/', body); }
  inspectRun(run) { return this.request('GET', `/api/test-management/runs/${run}/`); }
  recover(run) { return this.request('POST', `/api/test-management/runs/${run}/recover/`, {}); }
  accounts(run) { return this.request('GET', `/api/test-management/runs/${run}/accounts/`); }
  createAccount(run, body) { return this.request('POST', `/api/test-management/runs/${run}/accounts/`, body); }
  inspectAccount(run, account) { return this.request('GET', `/api/test-management/runs/${run}/accounts/${account}/`); }
  async withRecoveryPage(run, account, page, usePage) {
    try {
      const result = await this.request('POST', `/api/test-management/runs/${run}/accounts/${account}/recovery-message/`, {});
      const target = new URL(result.link);
      if (target.origin !== this.baseURL || !/^\/reset\/[^/]+\/[^/]+\/?$/.test(target.pathname)) throw new Error('Invalid recovery destination');
      await page.goto(target.href);
      await usePage(page);
      return async () => { await page.goto(target.href); };
    } catch (cause) {
      const error = new Error('Test management request failed');
      error.code = cause.code;
      throw error;
    }
  }
  updateAccount(run, account, body) { return this.request('PATCH', `/api/test-management/runs/${run}/accounts/${account}/`, body); }
  fixture(run, body) { return this.request('POST', `/api/test-management/runs/${run}/fixtures/`, body); }

  async login(run, account, email, password) {
    const context = await this.browser.newContext({ baseURL: this.baseURL });
    try {
      const csrfResponse = await context.request.get('/api/csrf/', { maxRedirects: 0 });
      if (!csrfResponse.ok()) throw new Error('CSRF preparation failed');
      const csrf = (await context.cookies()).find((cookie) => cookie.name === 'csrftoken')?.value;
      if (!csrf) throw new Error('CSRF preparation failed');
      const response = await context.request.post('/api/auth/browser/v1/auth/login', {
        data: { email, password }, headers: { 'X-CSRFToken': csrf }, maxRedirects: 0,
      });
      if (!response.ok()) throw new Error('Ordinary login failed');
      const handle = randomUUID();
      this.sessions.set(handle, { context, run, account });
      return handle;
    } catch (error) {
      await context.close();
      throw error;
    }
  }

  context(handle) {
    const session = this.sessions.get(handle);
    if (!session) throw new Error('Unknown session handle');
    return session.context;
  }

  async disposeSessions(predicate = () => true) {
    const contexts = [];
    for (const [handle, session] of this.sessions) {
      if (predicate(session)) { this.sessions.delete(handle); contexts.push(session.context.close()); }
    }
    await Promise.all(contexts);
  }

  async deleteAccount(run, account) {
    try { return await this.request('DELETE', `/api/test-management/runs/${run}/accounts/${account}/`); }
    finally { await this.disposeSessions((item) => item.run === run && item.account === account); }
  }

  async reset(run) {
    try { return await this.request('POST', `/api/test-management/runs/${run}/reset/`, {}); }
    finally { await this.disposeSessions((item) => item.run === run); }
  }

  async close(run) {
    try { return await this.request('POST', `/api/test-management/runs/${run}/close/`, {}); }
    finally { await this.disposeSessions((item) => item.run === run); }
  }

  async dispose() { await this.disposeSessions(); await this.controller.dispose(); }
}
