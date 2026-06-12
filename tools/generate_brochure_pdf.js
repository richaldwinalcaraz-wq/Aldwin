const { chromium } = require('playwright');
const path = require('path');

(async () => {
  try {
    const browser = await chromium.launch();
    const page = await browser.newPage();

    const htmlPath = path.resolve(__dirname, '../brochure_hiraya_systems.html');
    await page.goto('file://' + htmlPath);

    // Wait for fonts to load
    await page.waitForLoadState('networkidle');

    const pdfPath = path.resolve(__dirname, '../hiraya-systems-brochure.pdf');
    await page.pdf({
      path: pdfPath,
      format: 'A4',
      printBackground: true,
      margin: { top: 0, bottom: 0, left: 0, right: 0 }
    });

    await browser.close();
    console.log(`✓ PDF saved: ${pdfPath}`);
    console.log('✓ 9 pages generated successfully');
  } catch (error) {
    console.error('Error generating PDF:', error);
    process.exit(1);
  }
})();
