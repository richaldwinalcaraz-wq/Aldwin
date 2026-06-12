# anonymize_dashboards.py
# Replaces all identifying details in Hiraya and NexaShop dashboards
# with generic placeholders for client-facing demos.
# Output: Client Demo folder under OneDrive Documents

import os

BASE = r"C:\Users\user\OneDrive\Documents"

JOBS = [
    {
        "name": "Construction Dashboard (Hiraya)",
        "source": os.path.join(BASE, "DashBoard Project", "index.html"),
        "output": os.path.join(BASE, "Client Demo", "Construction Dashboard", "index.html"),
        # Ordered list of (find, replace) — longer/more-specific strings FIRST
        "replacements": [
            # --- All-caps brand (CSS/JS comments, HTML text nodes) ---
            ("HIRAYA PREMIUM — Design Token System", "YOUR COMPANY — Design Token System"),
            ("HIRAYA PREMIUM OVERRIDE — loaded AFTER Tailwind CDN", "YOUR COMPANY OVERRIDE — loaded AFTER Tailwind CDN"),
            ("HIRAYA CONSTRUCTION SUPPLY", "YOUR COMPANY NAME"),
            ("HIRAYA", "YOUR COMPANY"),

            # --- Standalone subtitle (login page, sidebar, JS defaults, contact form) ---
            ("Construction Supply", "Your Company"),

            # --- Password hint ---
            ("hiraya2024", "demo2024"),

            # --- Logo fallback letter ---
            ("textContent:'H'", "textContent:'YC'"),

            # --- White-label form placeholders ---
            ('placeholder="e.g. HIRAYA"', 'placeholder="e.g. YOUR COMPANY"'),
            ('placeholder="e.g. Construction Supply"', 'placeholder="e.g. Your Company"'),

            # --- JS default values ---
            ("companyName:'HIRAYA'", "companyName:'YOUR COMPANY'"),
            ("|| 'HIRAYA'", "|| 'YOUR COMPANY'"),
            ("|| 'Construction Supply'", "|| 'Your Company'"),

            # --- Page title / brand strings (most specific first) ---
            ("Hiraya Construction Supply — Dashboard", "Your Company — Dashboard"),
            ("Hiraya Construction Supply", "Your Company Name"),
            ("Hiraya CRM", "Your CRM"),
            ("Hiraya AI Assistant", "Your AI Assistant"),
            ("Contact Hiraya", "Contact Us"),
            ("@hiraya.com", "@yourcompany.com"),
            ("Hiraya", "Your Company"),

            # --- Employee emails (before generic @hiraya catch) ---
            ("j.davis@yourcompany.com", "emp01@yourcompany.com"),
            ("m.sullivan@yourcompany.com", "emp02@yourcompany.com"),
            ("p.reynolds@yourcompany.com", "emp03@yourcompany.com"),
            ("a.grant@yourcompany.com", "emp04@yourcompany.com"),
            ("j.mitchell@yourcompany.com", "emp05@yourcompany.com"),
            ("r.baker@yourcompany.com", "emp06@yourcompany.com"),
            ("c.vargas@yourcompany.com", "emp07@yourcompany.com"),
            ("l.foster@yourcompany.com", "emp08@yourcompany.com"),
            ("m.torres@yourcompany.com", "emp09@yourcompany.com"),
            ("e.carter@yourcompany.com", "emp10@yourcompany.com"),

            # --- Products (longest / most-specific first) ---
            ("Portland Cement 40kg", "Item 1 (40kg)"),
            ("Portland Cement", "Item 1"),
            ("Portland Cem", "Item 1"),
            ("Masonry Cement", "Item 10"),
            ("Masonry Cem", "Item 10"),
            ("Steel Bar 10mm", "Item 2A"),
            ("Steel Bar 12mm", "Item 2B"),
            ("Steel Bar 16mm", "Item 2C"),
            ("Steel Bar", "Item 2"),
            ('Hollow Blocks 4"', "Item 3A"),
            ('Hollow Blocks 6"', "Item 3B"),
            ('Hollow Blk 4"', "Item 3A"),
            ('Hollow Blk 6"', "Item 3B"),
            ("Hollow Blk", "Item 3"),
            ("River Sand", "Item 4"),
            ('Gravel 3/4"', "Item 5"),
            ("Gravel", "Item 5"),
            ('Plywood 3/4"', "Item 6"),
            ("Plywood", "Item 6"),
            ("GI Sheet 26GA", "Item 7A"),
            ("GI Sheet 24GA", "Item 7B"),
            ("GI Sheet", "Item 7"),
            ("Rebar Tie Wire", "Item 8"),
            ("CHB Mortar", "Item 9"),
            ("Lumber 2x3", "Item 11"),
            ("Lumber", "Item 11"),
            # Hollow Blocks without size suffix (in order product strings)
            ("Hollow Blocks", "Item 3"),
            # Sand as standalone product in order strings (River Sand already handled above)
            ("Sand 15m3", "Item 4 15m3"),
            ("Sand 5m\u00b3", "Item 4 5m\u00b3"),
            ("Sand 8m\u00b3", "Item 4 8m\u00b3"),
            (", Sand", ", Item 4"),

            # --- Categories (chart labels) ---
            ("Aggregates", "Category C"),
            ("Wood & Metal", "Category E"),
            ("Wood/Metal", "Category E"),
            ("Masonry", "Category D"),
            ("Cement", "Category A"),
            ("Steel", "Category B"),

            # --- Employees ---
            ("James Davis", "Employee 1"),
            ("Mary Sullivan", "Employee 2"),
            ("Peter Reynolds", "Employee 3"),
            ("Anna Grant", "Employee 4"),
            ("Joe Mitchell", "Employee 5"),
            ("Rose Baker", "Employee 6"),
            ("Chris Vargas", "Employee 7"),
            ("Linda Foster", "Employee 8"),
            ("Michael Torres", "Employee 9"),
            ("Elena Carter", "Employee 10"),

            # --- Emergency contacts ---
            ("Carol Davis", "Emergency Contact 1"),
            ("Robert Sullivan", "Emergency Contact 2"),
            ("Louise Reynolds", "Emergency Contact 3"),
            ("Mark Grant", "Emergency Contact 4"),
            ("Nancy Mitchell", "Emergency Contact 5"),
            ("Ernest Baker", "Emergency Contact 6"),
            ("Tina Vargas", "Emergency Contact 7"),
            ("Gary Foster", "Emergency Contact 8"),
            ("Laura Torres", "Emergency Contact 9"),
            ("Ben Carter", "Emergency Contact 10"),

            # --- CRM contact persons (before email replacements) ---
            ("Mark Steele", "Contact 5"),
            ("Ryan Owen", "Contact 1"),
            ("Carla Turner", "Contact 2"),
            ("Ben Cross", "Contact 3"),
            ("Diana Lane", "Contact 4"),
            ("Gina Ross", "Contact 6"),
            ("Raul Gordon", "Contact 7"),
            ("Joy Stone", "Contact 8"),
            ("Leo Tanner", "Contact 9"),
            ("Pete Vance", "Contact 10"),
            ("Alex Burns", "Contact 11"),
            ("Paul Stone", "Contact 12"),
            ("Rex Richards", "Contact 13"),
            ("Nathan Adams", "Contact 14"),
            ("Grace Tyler", "Contact 15"),
            ("Rich Morgan", "Contact 16"),

            # --- CRM contact emails (before domain-only catch-alls) ---
            ("alex.burns@abcconstruction.com", "contact01@client1.com"),
            ("paul.stone@summitbuilders.com", "contact02@client8.com"),
            ("rex.richards@ridgedevgroup.com", "contact03@client7.com"),
            ("nathan.adams@nationalbuilders.com", "contact04@client2.com"),
            ("grace.tyler@greentech.com", "contact05@client3.com"),
            ("pete.vance@alliedcontractors.com", "contact06@client9.com"),
            ("gina.ross@prosupplyco.com", "contact07@leadco6.com"),
            ("rich.morgan@metroconstruction.com", "contact08@client4.com"),

            # --- Phone numbers (employee work phones) ---
            ("(617) 555-4001", "(000) 555-0001"),
            ("(617) 555-4002", "(000) 555-0002"),
            ("(617) 555-4003", "(000) 555-0003"),
            ("(617) 555-4004", "(000) 555-0004"),
            ("(617) 555-4005", "(000) 555-0005"),
            ("(617) 555-4006", "(000) 555-0006"),
            ("(617) 555-4007", "(000) 555-0007"),
            ("(617) 555-4008", "(000) 555-0008"),
            ("(617) 555-4009", "(000) 555-0009"),
            ("(617) 555-4010", "(000) 555-0010"),

            # --- Phone numbers (emergency contact phones) ---
            ("(617) 555-2001", "(000) 555-1001"),
            ("(617) 555-2002", "(000) 555-1002"),
            ("(617) 555-2003", "(000) 555-1003"),
            ("(617) 555-2004", "(000) 555-1004"),
            ("(617) 555-2005", "(000) 555-1005"),
            ("(617) 555-2006", "(000) 555-1006"),
            ("(617) 555-2007", "(000) 555-1007"),
            ("(617) 555-2008", "(000) 555-1008"),
            ("(617) 555-2009", "(000) 555-1009"),
            ("(617) 555-2010", "(000) 555-1010"),

            # --- Phone numbers (CRM contacts phones: 555-3xxx) ---
            ("(617) 555-3001", "(000) 555-3001"),
            ("(617) 555-3002", "(000) 555-3002"),
            ("(617) 555-3003", "(000) 555-3003"),
            ("(617) 555-3004", "(000) 555-3004"),
            ("(617) 555-3005", "(000) 555-3005"),
            ("(617) 555-3006", "(000) 555-3006"),
            ("(617) 555-3007", "(000) 555-3007"),
            ("(617) 555-3008", "(000) 555-3008"),

            # --- Phone numbers (Leads table: 555-8xxx) ---
            ("(617) 555-8001", "(000) 555-4001"),
            ("(617) 555-8002", "(000) 555-4002"),
            ("(617) 555-8003", "(000) 555-4003"),
            ("(617) 555-8004", "(000) 555-4004"),
            ("(617) 555-8005", "(000) 555-4005"),
            ("(617) 555-8006", "(000) 555-4006"),
            ("(617) 555-8007", "(000) 555-4007"),
            ("(617) 555-8008", "(000) 555-4008"),
            ("(617) 555-8009", "(000) 555-4009"),
            ("(617) 555-8010", "(000) 555-4010"),

            # --- Client companies (longest first) ---
            ("Ridge Development Group", "Client 7"),
            ("National Builders Inc", "Client 2"),
            ("GreenTech Construction", "Client 3"),
            ("Pacific Builders Corp", "Client 6"),
            ("Allied Contractors LLC", "Client 9"),
            ("Golden Gate Contractors", "Client 11"),
            ("ABC Construction Corp", "Client 1"),
            ("Metro Construction", "Client 4"),
            ("LJ Builders Corp", "Client 5"),
            ("Fortaleza Construction", "Client 10"),
            ("Summit Builders", "Client 8"),

            # --- Additional lead companies (in Leads table, not in original orders list) ---
            ("Sunrise Development Inc", "Lead Company 2"),
            ("Metro Infra Solutions", "Lead Company 3"),
            ("Lakeview Homes Builder", "Lead Company 4"),
            ("Pro Supply Co.", "Lead Company 6"),
            ("Valley Build Corp", "Lead Company 7"),
            ("Northstar Properties", "Lead Company 8"),
            ("Greenfield Estates", "Lead Company 9"),

            # --- "ABC Construction" without Corp suffix (activity note) ---
            ("ABC Construction", "Client 1"),
            # --- "Pacific Builders" without Corp suffix (activity notes, form placeholder) ---
            ("Pacific Builders", "Client 6"),
        ],
    },
    {
        "name": "Ecommerce Dashboard (NexaShop)",
        "source": os.path.join(BASE, "NexaShop Dashboard", "index.html"),
        "output": os.path.join(BASE, "Client Demo", "Ecommerce Dashboard", "index.html"),
        "replacements": [
            # --- Brand (most specific first) ---
            ("NexaShop \u2014 E-Commerce Dashboard", "Your Brand \u2014 E-Commerce Dashboard"),
            ("\u00a9 2026 NexaShop. All rights reserved.", "\u00a9 2026 Your Brand. All rights reserved."),
            ("business assistant for NexaShop", "business assistant for Your Brand"),
            ("your NexaShop AI Assistant", "your Brand AI Assistant"),
            ("NexaShop", "Your Brand"),

            # --- Products ---
            ("Classic White Tee", "Item 1"),
            ("Denim Jacket", "Item 2"),
            ("Running Shoes", "Item 3"),
            ("Leather Wallet", "Item 4"),
            ("Canvas Tote Bag", "Item 5"),
            ("Snapback Cap", "Item 6"),
            ("Compression Socks", "Item 7"),
            ("Sport Shorts", "Item 8"),

            # --- SKUs ---
            ("CWT-001", "SKU-001"),
            ("DJ-001", "SKU-002"),
            ("RS-001", "SKU-003"),
            ("LW-001", "SKU-004"),
            ("CTB-001", "SKU-005"),
            ("SC-001", "SKU-006"),
            ("CS-001", "SKU-007"),
            ("SS-001", "SKU-008"),

            # --- Categories (longest first to avoid partial matches) ---
            ("Topwear", "Category 1"),
            ("Outerwear", "Category 2"),
            ("Footwear", "Category 3"),
            ("Accessories", "Category 4"),
            ("Bottoms", "Category 5"),
            ("Bags", "Category 6"),
            ("Tops", "Category 1"),
            ("Socks", "Category 7"),

            # --- Customer emails (before name replacement) ---
            ("maria.santos@email.com", "customer01@email.com"),
            ("juan.delacruz@email.com", "customer02@email.com"),
            ("ana.reyes@email.com", "customer03@email.com"),
            ("carlo.dizon@email.com", "customer04@email.com"),
            ("lea.mendoza@email.com", "customer05@email.com"),
            ("jose.ramirez@email.com", "customer06@email.com"),
            ("sofia.lim@email.com", "customer07@email.com"),

            # --- Customers (longest first) ---
            ("Juan dela Cruz", "Customer 2"),
            ("Maria Santos", "Customer 1"),
            ("Ana Reyes", "Customer 3"),
            ("Carlo Dizon", "Customer 4"),
            ("Lea Mendoza", "Customer 5"),
            ("Jose Ramirez", "Customer 6"),
            ("Sofia Lim", "Customer 7"),

            # --- Customer phone numbers ---
            ("09171234567", "09000000001"),
            ("09182345678", "09000000002"),
            ("09193456789", "09000000003"),
            ("09204567890", "09000000004"),
            ("09215678901", "09000000005"),

            # --- Suppliers ---
            ("Fabric World PH", "Supplier 1"),
            ("DenimCo Manila", "Supplier 2"),
            ("SportGear PH", "Supplier 3"),
            ("LeatherCraft PH", "Supplier 4"),
            ("EcoGoods PH", "Supplier 5"),
            ("CapZone MNL", "Supplier 6"),

            # --- Addresses ---
            ("123 Rizal St, Quezon City", "123 Main St, City 1"),
            ("456 Mabini St, Manila", "456 Main St, City 2"),
            ("789 Aguinaldo Ave, Caloocan", "789 Main Ave, City 3"),
            ("234 Bonifacio Dr, Makati", "234 Main Dr, City 4"),
            ("567 Luna St, Pasig", "567 Main St, City 5"),
            ("890 Osmena St, Cebu", "890 Main St, City 6"),
            ("321 Quezon Blvd, Manila", "321 Main Blvd, City 7"),
        ],
    },
]


def anonymize(job):
    src = job["source"]
    dst = job["output"]
    replacements = job["replacements"]

    print(f"\n{'='*60}")
    print(f"Processing: {job['name']}")
    print(f"  Source : {src}")
    print(f"  Output : {dst}")

    with open(src, "r", encoding="utf-8") as f:
        content = f.read()

    total = 0
    for find, replace in replacements:
        count = content.count(find)
        if count:
            content = content.replace(find, replace)
            print(f"  [{count:3d}x] '{find}' → '{replace}'")
            total += count

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  Done — {total} replacements applied.")
    return total


if __name__ == "__main__":
    grand_total = 0
    for job in JOBS:
        grand_total += anonymize(job)
    print(f"\n{'='*60}")
    print(f"All done. Total replacements across both files: {grand_total}")
    print(f"Output folder: {os.path.join(BASE, 'Client Demo')}")
