"use strict";

(function() {

    const timeUnits = [
        {'millis': 1000, 'limit': 60, 'singular': 'second', 'plural': 'seconds'},
        {'millis': 60000, 'limit': 60, 'singular': 'minute', 'plural': 'minutes'},
        {'millis': 3600000, 'limit': 24, 'singular': 'hour', 'plural': 'hours'},
        {'millis': 86400000, 'limit': 100, 'singular': 'day', 'plural': 'days'},
        false
    ];

    function updateTimeElements() {
        let timeElements = document.getElementsByTagName('time');
        let timeout = 86400000;
        for (let timeElement of timeElements) {
            let date = new Date(timeElement.getAttribute('datetime'));
            let now = new Date();
            let difference = now.getTime() - date.getTime();
            for (let timeUnit of timeUnits) {
                if (!timeUnit) {
                    timeElement.innerText = date.getFullYear() + '-' + (date.getMonth() + 1).toString().padStart(2, 0);
                    break;
                } else if (difference < timeUnit['millis'] * timeUnit['limit']) {
                    let units = Math.floor(difference / timeUnit['millis']);
                    let text = units + ' ' + (units == 1 ? timeUnit['singular'] : timeUnit['plural']) + ' ago';
                    timeElement.innerText = text;
                    timeout = Math.min(timeout, timeUnit['millis']);
                    break;
                }
            }
        }
        setTimeout(updateTimeElements, timeout);
    }

    window.addEventListener('load', updateTimeElements);

})();
