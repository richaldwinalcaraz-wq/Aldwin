const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('https://hiraya-v3.vercel.app/', { waitUntil: 'networkidle' });
  
  // Take screenshot
  await page.screenshot({ path: './hiraya_screenshot.png', fullPage: true });
  
  // Extract page structure
  const design = await page.evaluate(() => {
    const colors = new Map();
    const elements = document.querySelectorAll('*');
    
    elements.forEach(el => {
      const computed = window.getComputedStyle(el);
      const bgColor = computed.backgroundColor;
      const color = computed.color;
      
      if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)') {
        colors.set(bgColor, (colors.get(bgColor) || 0) + 1);
      }
    });
    
    return {
      title: document.title,
      h1: document.querySelector('h1')?.textContent || '',
      h2s: Array.from(document.querySelectorAll('h2')).map(h => h.textContent),
      buttons: Array.from(document.querySelectorAll('button')).map(b => b.textContent),
      topColors: Array.from(colors.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([color, count]) => ({ color, freq: count }))
    };
  });
  
  console.log(JSON.stringify(design, null, 2));
  
  await browser.close();
})();
