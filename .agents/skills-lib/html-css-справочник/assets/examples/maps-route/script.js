function initMap(){
    const map=new google.maps.Map(document.getElementById('map'),{
        zoom:10,
        center:{lat:25.2048,lng:55.2708}
    });
    const start={lat:25.1972,lng:55.2744};
    const end={lat:25.2048,lng:55.2708};
    new google.maps.Marker({position:start,map:map,title:'Start: Dubai Marina'});
    new google.maps.Marker({position:end,map:map,title:'End: Desert Camp'});
}
window.addEventListener('load',initMap);
