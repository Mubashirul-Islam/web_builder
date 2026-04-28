from website.models import Page, Website

def js_snippet(website: Website, page: Page) -> str:
    return f"""
console.log("Script loaded after build");

async function loadProperties() {{
const section = document.getElementById("properties");

try {{
const res = await fetch("http://127.0.0.1:8000/media/production/{website.name}/live/pages/{page.slug}.json");
const data = await res.json();

const propertyList = data.property_list || {{}};
const items = propertyList.item_list || [];

// Determine layout
const isGrid = propertyList.orientation === "grid";

// Apply layout config
section.className = isGrid ? "grid-view" : "list-view";

if (isGrid) {{
    section.style.setProperty(
    "--cols",
    propertyList.items_per_row || 4
    );
}}

// Build cards
const html = items.map(item => `
    <div class="card">
    <img src="${{item.image}}" alt="${{item.title}}" />

    <div class="card-body">
        <h3>${{item.title}}</h3>

        <p class="location">📍 ${{item.location}}</p>

        <p class="price">
        ${{item.currency}} ${{item.price}}
        </p>

        <p class="rating">
        ⭐ ${{item.rating}} (${{item.reviews}})
        </p>

        <div class="features">
        ${{item.features.map(f => `<span>${{f}}</span>`).join(" ")}}
        </div>

        <small class="provider">
        ${{item.provider_label}}
        </small>

        ${{item.is_new ? `<span class="badge">NEW</span>` : ""}}
    </div>
    </div>
`).join("");

section.innerHTML = `
    <div class="container">
    ${{html}}
    </div>
`;

}} catch (err) {{
console.error("Failed to load properties:", err);
section.innerHTML = "<p>Failed to load properties.</p>";
}}
}}

// run on page load
loadProperties();
"""