const images=[
{url:'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22200%22%3E%3Crect fill=%22%23FF6B35%22 width=%22300%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22white%22 font-size=%2224%22%3EDesert%3C/text%3E%3C/svg%3E',caption:'Golden Dunes'},
{url:'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22200%22%3E%3Crect fill=%22%23667eea%22 width=%22300%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22white%22 font-size=%2224%22%3ESunset%3C/text%3E%3C/svg%3E',caption:'Evening View'},
{url:'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22200%22%3E%3Crect fill=%22%231A1A2E%22 width=%22300%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22white%22 font-size=%2224%22%3ENight%3C/text%3E%3C/svg%3E',caption:'Starry Sky'}
];
function loadGallery(){document.getElementById('gallery').innerHTML=images.map((img,i)=>`<img src="${img.url}" onclick="openModal(${i})">`).join('');}
function openModal(i){document.getElementById('modal').style.display='block';document.getElementById('modalImg').src=images[i].url;document.getElementById('caption').textContent=images[i].caption;}
function closeModal(){document.getElementById('modal').style.display='none';}
document.addEventListener('DOMContentLoaded',loadGallery);
