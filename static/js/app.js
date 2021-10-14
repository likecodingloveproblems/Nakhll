if ('serviceWorker' in navigator) {
    navigator
        .serviceWorker
        .register('static/js/service-worker.js')
        .then(registration => {
            
            
            var serviceWorker;
            if (registration.installing) {
                serviceWorker = registration.installing;
                // document.querySelector('#kind').textContent = 'installing';
            } else if (registration.waiting) {
                serviceWorker = registration.waiting;
                // document.querySelector('#kind').textContent = 'waiting';
            } else if (registration.active) {
                serviceWorker = registration.active;
                // document.querySelector('#kind').textContent = 'active';
            }
            if (serviceWorker) {
                // logState(serviceWorker.state);
                serviceWorker.addEventListener('statechange', function (e) {
                    // logState(e.target.state);
                });
            }
        })
        .catch((err) => {
            console.log('SERVICE WORKER NOT REGISTRATION ==>', err);
        })
} else {
    console.log('SERVICE WORKER NOT SUPPORTED');
}



// getMediaDevices();