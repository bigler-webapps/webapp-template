// Supervisor retrieves the fixture; collaborator cannot update its role.
// Replace these account templates and fixture with your app's permission examples.
import { expect, test } from '@playwright/test';
import { randomBytes, randomUUID } from 'node:crypto';
import { TestManagementClient } from './test-management-client.js';

test.use({ trace: 'off', screenshot: 'off', video: 'off' });
test.setTimeout(300000);

test('supervisor and collaborator have distinct user access', async ({ browser }) => {
  const project = process.env.TEST_MANAGEMENT_PROJECT;
  const baseURL = process.env.TEST_MANAGEMENT_BASE_URL;
  expect(project).toBeTruthy();
  expect(baseURL).toBeTruthy();
  const client = new TestManagementClient(project, baseURL, browser);
  let run;
  try {
    const discovery = await client.discovery();
    expect(discovery.templates.map((item) => item.name)).toEqual(expect.arrayContaining(['supervisor', 'collaborator']));
    run = await client.createRun({ idempotency_key: randomUUID() });
    const make = async (template) => {
      const username = `tm-${randomBytes(8).toString('hex')}`;
      const email = `${username}@example.test`;
      const password = `Aa9!${randomBytes(24).toString('base64url')}`;
      const account = await client.createAccount(run.handle, { idempotency_key: randomUUID(), template,
        synthetic_identity: { username, email, name: username }, password });
      const session = await client.login(run.handle, account.handle, email, password);
      return { account, context: client.context(session) };
    };
    const supervisor = await make('supervisor');
    const collaborator = await make('collaborator');
    const fixture = await client.fixture(run.handle, { idempotency_key: randomUUID(), name: 'managed-user', parameters: { supervisor: supervisor.account.handle } });
    const path = `/api/users/${fixture.state.user_id}/`;
    const beforeResponse = await supervisor.context.request.get(path);
    expect(beforeResponse.status()).toBe(200);
    const before = await beforeResponse.json();
    expect(before.username).toBe(fixture.state.username);
    expect(before.role).toBe('none');
    const csrf = (await collaborator.context.cookies()).find((cookie) => cookie.name === 'csrftoken')?.value;
    expect(csrf).toBeTruthy();
    const refused = await collaborator.context.request.patch(`${path}update-role/`, {
      data: { role: 'collaborator' }, headers: { 'X-CSRFToken': csrf },
    });
    expect(refused.status()).toBe(404);
    const afterResponse = await supervisor.context.request.get(path);
    expect(afterResponse.status()).toBe(200);
    expect(await afterResponse.json()).toEqual(before);
    const page = await supervisor.context.newPage();
    await page.goto('/account?tab=users');
    expect(await page.evaluate(async () => (await fetch('/api/test-management/discovery/')).status)).toBe(404);
    const oldRun = run.handle;
    await client.close(oldRun);
    run = undefined;
    const closed = await client.inspectRun(oldRun).then(() => null, (error) => error);
    expect(closed).not.toBeNull();
    expect(closed.status).toBeGreaterThanOrEqual(400);
    expect(closed.status).toBeLessThan(500);
  } finally {
    if (run) await client.close(run.handle);
    await client.dispose();
  }
});
