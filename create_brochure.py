import os

# Remove old file if it exists
if os.path.exists('hiraya-sales-brochure.html'):
    os.remove('hiraya-sales-brochure.html')

html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hiraya Systems | AI-Powered Operations</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0a0a0f; color: #f0ede8; line-height: 1.6; overflow-x: hidden; }
        nav { position: fixed; top: 0; width: 100%; padding: 1.5rem 2rem; background: rgba(10, 10, 15, 0.95); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(240, 237, 232, 0.1); display: flex; justify-content: space-between; align-items: center; z-index: 100; }
        .logo { font-size: 1.5rem; font-weight: bold; letter-spacing: 2px; }
        nav a { color: #f0ede8; text-decoration: none; margin: 0 1.5rem; font-size: 0.9rem; transition: opacity 0.3s; }
        nav a:hover { opacity: 0.7; }
        .nav-cta { background: linear-gradient(135deg, #ff6b6b, #ff8c42); padding: 0.75rem 1.5rem; border-radius: 4px; font-size: 0.9rem; cursor: pointer; border: none; color: white; transition: transform 0.3s; }
        .nav-cta:hover { transform: translateY(-2px); }
        .hero { margin-top: 80px; min-height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; padding: 2rem; }
        .orb { position: absolute; border-radius: 50%; filter: blur(40px); opacity: 0.6; }
        .orb-1 { width: 400px; height: 400px; background: linear-gradient(135deg, #ff6b6b, #ff8c42); top: -100px; left: -100px; animation: float 20s ease-in-out infinite; }
        .orb-2 { width: 300px; height: 300px; background: linear-gradient(135deg, #00d4ff, #0099ff); bottom: 100px; right: -50px; animation: float 15s ease-in-out infinite reverse; }
        @keyframes float { 0%, 100% { transform: translate(0, 0); } 50% { transform: translate(50px, 50px); } }
        .hero-content { position: relative; z-index: 10; text-align: center; max-width: 800px; }
        .hero h1 { font-size: 4rem; font-weight: 900; margin-bottom: 1.5rem; line-height: 1.1; text-transform: uppercase; letter-spacing: -1px; }
        .hero p { font-size: 1.3rem; margin-bottom: 2rem; color: rgba(240, 237, 232, 0.8); line-height: 1.8; }
        .cta-primary { display: inline-block; background: linear-gradient(135deg, #ff6b6b, #ff8c42); color: white; padding: 1rem 2.5rem; border-radius: 4px; text-decoration: none; font-size: 1.1rem; font-weight: 600; transition: all 0.3s; border: none; cursor: pointer; }
        .cta-primary:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3); }
        .features { padding: 6rem 2rem; max-width: 1200px; margin: 0 auto; position: relative; z-index: 5; }
        .section-title { font-size: 2.5rem; margin-bottom: 3rem; text-align: center; font-weight: 700; }
        .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
        .feature-card { background: rgba(240, 237, 232, 0.05); padding: 2rem; border-radius: 8px; border: 1px solid rgba(240, 237, 232, 0.1); transition: all 0.3s; }
        .feature-card:hover { border-color: rgba(255, 107, 107, 0.3); background: rgba(240, 237, 232, 0.08); transform: translateY(-5px); }
        .feature-icon { font-size: 2.5rem; margin-bottom: 1rem; }
        .feature-card h3 { font-size: 1.3rem; margin-bottom: 0.75rem; font-weight: 600; }
        .feature-card p { color: rgba(240, 237, 232, 0.7); font-size: 0.95rem; }
        .proof { padding: 6rem 2rem; background: rgba(240, 237, 232, 0.02); max-width: 1200px; margin: 0 auto; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; margin-top: 2rem; }
        .stat-card { text-align: center; }
        .stat-number { font-size: 3rem; font-weight: 900; background: linear-gradient(135deg, #ff6b6b, #ff8c42); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .stat-label { color: rgba(240, 237, 232, 0.7); margin-top: 0.5rem; font-size: 0.95rem; }
        .cta-section { padding: 6rem 2rem; text-align: center; position: relative; overflow: hidden; }
        .cta-section::before { content: ""; position: absolute; top: -50%; right: -50%; width: 600px; height: 600px; background: linear-gradient(135deg, #00d4ff, #0099ff); border-radius: 50%; filter: blur(60px); opacity: 0.2; }
        .cta-content { position: relative; z-index: 5; max-width: 600px; margin: 0 auto; }
        .cta-section h2 { font-size: 2.5rem; margin-bottom: 1rem; font-weight: 700; }
        .cta-section p { font-size: 1.1rem; color: rgba(240, 237, 232, 0.8); margin-bottom: 2rem; }
        footer { padding: 3rem 2rem; border-top: 1px solid rgba(240, 237, 232, 0.1); text-align: center; color: rgba(240, 237, 232, 0.5); font-size: 0.9rem; }
        @media (max-width: 768px) { .hero h1 { font-size: 2.5rem; } .hero p { font-size: 1rem; } .section-title { font-size: 1.8rem; } nav { flex-direction: column; gap: 1rem; } nav a { margin: 0.5rem 0; } }
    </style>
</head>
<body>
    <nav>
        <div class="logo">HIRAYA</div>
        <div style="display: flex; gap: 2rem; align-items: center;">
            <a href="#features">Features</a>
            <a href="#proof">Results</a>
            <a href="#cta">Contact</a>
            <button class="nav-cta">Book a Call</button>
        </div>
    </nav>

    <section class="hero">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="hero-content">
            <h1>Your Competitors Aren't Waiting.<br>Neither Should You.</h1>
            <p>Automate your business operations with AI-powered systems. Transform repetitive work into strategic advantage in weeks, not months.</p>
            <button class="cta-primary">Start Your Free Discovery Call</button>
        </div>
    </section>

    <section class="features" id="features">
        <h2 class="section-title">Six Systems. One Integrated Operation.</h2>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <h3>Agentic AI Chatbots</h3>
                <p>24/7 customer support that learns your business. Handle inquiries, process orders, and resolve issues automatically.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚙️</div>
                <h3>Workflow Automation</h3>
                <p>Eliminate manual data entry. Automate across your entire tech stack—CRM, email, spreadsheets, everything.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📈</div>
                <h3>Sales Funnels</h3>
                <p>High-converting landing pages that close deals. Built for your unique value proposition, not templates.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>Business Dashboards</h3>
                <p>Real-time visibility into your operations. Make data-driven decisions with custom analytics and reporting.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔗</div>
                <h3>CRM Integration</h3>
                <p>Seamless data flow between your systems. Your CRM becomes the source of truth for the entire business.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎨</div>
                <h3>Custom Website Design</h3>
                <p>Brands that convert. Modern, fast, and optimized for your target customer from day one.</p>
            </div>
        </div>
    </section>

    <section class="proof" id="proof">
        <h2 class="section-title">Why Teams Choose Hiraya</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">40%</div>
                <div class="stat-label">Avg. time saved on operations</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">3x</div>
                <div class="stat-label">Faster system deployment</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">0</div>
                <div class="stat-label">Account managers. You work with builders.</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">100%</div>
                <div class="stat-label">Custom to your business</div>
            </div>
        </div>
    </section>

    <section class="cta-section" id="cta">
        <div class="cta-content">
            <h2>Map Your Operation. Transform Your Business.</h2>
            <p>We spend time understanding your business before writing a single line of code. That's how we deliver systems that actually work.</p>
            <button class="cta-primary">Book a Free Discovery Call</button>
        </div>
    </section>

    <footer>
        <p>&copy; 2026 Hiraya Systems. All rights reserved. | hello@hiraya.systems</p>
    </footer>
</body>
</html>'''

with open('hiraya-sales-brochure.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('✓ Created hiraya-sales-brochure.html with dark theme (hiraya-v3 design)')
