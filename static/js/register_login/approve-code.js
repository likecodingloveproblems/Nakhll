let elButton = document.querySelector('#sendCode-btn');
let storage = window.localStorage;
let countDownStorage, countDownCallStorage;

//add attribute element
let handleSetAttr = (el, attr, status) => {
    el.setAttribute(attr, status);
}
//remove attribute element
let handleremovAttr = (el, attr) => {
    el.removeAttribute(attr)
}
//change text element
let handleChangeText = (el, text) => {
    el.textContent = text;
}
window.addEventListener('DOMContentLoaded', function () {
    // handleSetAttr(elButton, 'disabled', true)
})

//down counter function
let countdown = (minutes, seconds) => {
    let timeoutHandle = null;
    let second = Number(seconds);
    let mins = Number(minutes);

    let tick = () => {
        let counter = document.getElementById("countDown");
        let current_minutes = mins;
        --second;
        storage.setItem('countDown', JSON.stringify({ minutes: current_minutes, seconds: (second < 10 ? 0 : "") + second })
        );

        counter.textContent =
            toFarsiNumber(current_minutes.toString()) + ":" + (second < 10 ? toFarsiNumber(0) : "") + String(toFarsiNumber(second));
        if (second > 0) {
            timeoutHandle = setTimeout(tick, 1000);
        }
        else if (current_minutes > 0) {
            countdown(current_minutes - 1, 59);
        }
        else {
            storage.setItem('countDown', JSON.stringify({ minutes: 0, seconds: 00 }));
            handleChangeText(elButton, 'ارسال مجدد کد یکبار مصرف');
            elButton.hasAttributes('disabled') ? handleremovAttr(elButton, 'disabled') : null;
        }
    }
    if (second > 0 || minutes > 0) {
        tick();
    }
}

//conditional countDown when refreshing window
if (JSON.parse(storage.getItem('countDown'))) {
    // debugger
    countDownStorage = JSON.parse(storage.getItem('countDown'));
    if (countDownStorage['seconds'] !== 0 || countDownStorage['minutes'] !== 0) {
        // handleChangeText(elButton, 'call ME');
        handleSetAttr(elButton, 'disabled', true)
        countdown(Number(countDownStorage['minutes']), Number(countDownStorage['seconds']));
    } else {
        handleChangeText(elButton, 'ارسال مجدد کد یکبار مصرف');
        console.log('elButton.hasAttributes', elButton.hasAttributes('disabled'))
        elButton.hasAttributes('disabled') ? handleremovAttr(elButton, 'disabled') : null;
    }
} else {
    countdown(1, 60);
}

//btn sending CODE and CALL 
elButton.onclick = (e) => {
    e.preventDefault();
    let getTextButton = elButton.textContent;
    countDownStorage = JSON.parse(storage.getItem('countDown'));

    handleSetAttr(elButton, 'disabled', true)
    countdown(1, 60);
}

//convert english to perssion
function toFarsiNumber(number) {
    const farsiDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return number
        .toString()
        .split('')
        .map(x => farsiDigits[x])
        .join('');
}

