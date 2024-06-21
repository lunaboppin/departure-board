// index.js
const express = require('express');
const puppeteer = require('puppeteer');

const app = express();
const PORT = process.env.PORT || 3042;

app.use(express.json());

// Define your API endpoint
app.post('/api/location', async (req, res) => {
    try {
        const { location } = req.body;
        const { x_amz_date, authorization } = await getCredentials(location);
        res.json({ x_amz_date, authorization });
    } catch (error) {
        console.error('An error occurred:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Function to retrieve credentials
async function getCredentials(location) {
    const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] });
    const page = await browser.newPage();
    await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/125.0.6422.141 Safari/537.36");

    const credentials = {};

    page.on('request', async (request) => {
        if (request.url().includes(`https://tiger-api.worldline.global/services/${location}`)) {
            if (request.method() === 'GET') {
                const headers = request.headers();
                credentials['x_amz_date'] = headers['x-amz-date'];
                credentials['authorization'] = headers['authorization'];
                console.log("Extracted Headers:");
                console.log(`x-amz-date: ${credentials['x_amz_date']}`);
                console.log(`Authorization: ${credentials['authorization']}`);
            }
            await request.continue();
        } else {
            await request.continue();
        }
    });

    await page.setRequestInterception(true);
    await page.goto(`https://tiger.worldline.global/${location}/ciss;graphic=1`);
    await new Promise(resolve => setTimeout(resolve, 20000));

    await browser.close();

    return { x_amz_date: credentials['x_amz_date'], authorization: credentials['authorization'] };
}

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
