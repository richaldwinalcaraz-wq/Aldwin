const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('https://hiraya-v3.vercel.app/', { waitUntil: 'networkidle' });
  
  // Get full HTML
  const html = await page.content();
  require('fs').writeFileSync('./hiraya_source.html', html);
  
  // Get all text content
  const text = await page.evaluate(() => document.body.innerText);
  require('fs').writeFileSync('./hiraya_content.txt', text);
  
  console.log('✓ Saved: hiraya_source.html');
  console.log('✓ Saved: hiraya_content.txt');
  console.log('\nPage content preview:');
  console.log(text.substring(0, 800));
  
  await browser.close();
})();
