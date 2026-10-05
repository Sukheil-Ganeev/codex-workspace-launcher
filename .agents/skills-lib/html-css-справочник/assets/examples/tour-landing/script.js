function bookTour(tourName) {
    alert('Booking: ' + tourName + '\nRedirecting to booking form...');
    document.getElementById('contact').scrollIntoView({behavior: 'smooth'});
}

function submitBooking(event) {
    event.preventDefault();
    alert('Tour booked successfully! We will contact you soon.');
    event.target.reset();
}
