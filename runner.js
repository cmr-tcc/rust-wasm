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
    const urlPath = request.url === '/' ? '/index.html' : request.url;
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
    args: ['--no-sandbox', '--disable-setuid-sandbox'] 
});
const page = await browser.newPage();

await page.goto(`http://localhost:${port}`);

await page.waitForFunction(
    () => window.__benchmarkResults !== undefined || window.__benchmarkError !== undefined,
    { timeout: 300_000 }
);

const results = await page.evaluate(
    () => window.__benchmarkResults ?? { error: window.__benchmarkError }
);

console.log(JSON.stringify(results, null, 2));

await browser.close();
server.close();
