const tours=[
{id:1,name:'Morning Safari',price:350,duration:'5h',features:['Sunrise','Breakfast','Camel ride']},
{id:2,name:'Evening Safari',price:420,duration:'6h',features:['Sunset','Dinner','Camel ride']},
{id:3,name:'Night Safari VIP',price:650,duration:'7h',features:['Full experience','Belly dance','Stars']}
];
function renderCards(){
    const html=tours.map(t=>`
        <div class="tour-card">
            <div class="card-image"></div>
            <div class="card-content">
                <h3>${t.name}</h3>
                <p>${t.duration}</p>
                <div class="card-price">${t.price} AED</div>
                <ul class="card-features">${t.features.map(f=>`<li>✓ ${f}</li>`).join('')}</ul>
                <button class="btn-card">Book Now</button>
            </div>
        </div>
    `).join('');
    document.getElementById('cardsContainer').innerHTML=html;
}
document.addEventListener('DOMContentLoaded',renderCards);
