import puppeteer from 'puppeteer';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const webDirectory = join(fileURLToPath(new URL('.', import.meta.url)), 'web');
const port = 8080;

const mimeTypes = {
    '.html': 'text/html; charset=utf-8',
    '.js':   'application/javascript; charset=utf-8',
    '.wasm': 'application/wasm',
};

const server = createServer(async (request, response) => {
    const requestUrl = new URL(request.url, `http://localhost:${port}`);

    const urlPath = requestUrl.pathname === '/'
        ? '/index.html'
        : requestUrl.pathname;

    const filePath = join(webDirectory, urlPath);

    try {
        const data = await readFile(filePath);
        response.writeHead(200, {
            'Content-Type': mimeTypes[extname(filePath)] ?? 'application/octet-stream',
            'Cross-Origin-Opener-Policy': 'same-origin',
            'Cross-Origin-Embedder-Policy': 'require-corp',
        });
        response.end(data);
    } catch {
        response.writeHead(404);
        response.end('Not found');
    }
});

server.listen(port);

const browser = await puppeteer.launch({ 
    headless: true, 
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    protocolTimeout: 600_000
});
const page = await browser.newPage();

const algorithm = process.argv[2];
const iterations = process.argv[3];
const warmUp = process.argv[4];
const parameter = process.argv[5];

await page.goto(
    `http://localhost:${port}?algorithm=${algorithm}&iterations=${iterations}&warm_up=${warmUp}&parameter=${parameter}`,
);

await page.waitForFunction(
    () => window.__benchmarkResult !== undefined || window.__benchmarkError !== undefined,
    { timeout: 600_000 }
);

const results = await page.evaluate(
    () => window.__benchmarkResult ?? { error: window.__benchmarkError }
);

const output = await page.evaluate(
    () => window.__benchmarkOutput
);

console.log(JSON.stringify(results, null, 2));

console.log(output);

await browser.close();
server.close();
