document.addEventListener('DOMContentLoaded', async () => {
    const url = 'http://localhost:8000/codeforces';
    const response = await fetch(url);
    //loading state
    let loader = document.getElementById('loader');
    loader.style.display = 'none';
    // error handling
    if (!response.ok) {
        let error = document.getElementById('error');
        error.style.display = 'block';
        return;
    }
    const resp = await response.json();
    let codeforces = resp.contests;
    console.log(codeforces)
    let contestList = document.getElementById('contestList');
    codeforces.forEach(contest => {
        let tr = document.createElement('tr');
        let name = document.createElement('td');
        let date = document.createElement('td');
        let duration = document.createElement('td');
        let link = document.createElement('td');
        // styling
        name.classList.add('px-2', 'py-2', 'text-left', 'text-blue-600', 'border', 'border-gray-600', 'font-bold', 'font-mono');
        date.classList.add('px-2', 'py-2', 'text-purple-600', 'border', 'border-gray-600', 'font-bold', 'font-mono');
        duration.classList.add('px-2', 'py-2', 'text-green-600', 'border', 'border-gray-600', 'font-bold', 'font-mono');
        link.classList.add('px-2', 'py-2', 'text-red-600', 'border', 'border-gray-600', 'font-bold','font-mono');
        // setting content
        name.textContent = contest.contest_name;
        let dateArr = contest.contest_date.split(' ');
        let timeString = dateArr[1].split(':');
        // add two 1/2 hours to the time
        let hour = parseInt(timeString[0]);
        let minute = parseInt(timeString[1]);
        minute += 30;
        if(minute >= 60){
            minute -= 60;
            hour += 1;
        }
        hour += 2;
        if(minute < 10) minute = '0' + minute;
        let newTime = hour + ':' + minute;
        date.textContent = ` ${dateArr[0]} ${newTime}`;
        //date.textContent = contest.contest_date;
        duration.textContent = contest.duration;
        let a = document.createElement('a');
        if(a.href !== "Not Available") a.href = contest.register_link;
        else a.href = 'https://codeforces.com/contests';
        a.textContent = 'Register';
        link.appendChild(a);
        tr.appendChild(name);
        tr.appendChild(date);
        tr.appendChild(duration);
        tr.appendChild(link);
        contestList.appendChild(tr);
    });
});