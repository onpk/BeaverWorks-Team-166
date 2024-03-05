const cats = ["Pets", "School", "Friends", "Sports", "Sarcasm", "Texting", "Summer", "Theater"];
const n = [12, 3, 2, 3, 1, 2, 18, 6];
const t = [20, 5, 3, 6, 3, 3, 20, 10];

for (let i = 0; i < cats.length; i++) {
    document.getElementById("i" + (i+1).toString()).textContent=cats[i].concat(" (", n[i].toString(), ")");
    var pn = document.getElementById("p" + (i+1).toString());
    pn.style.width = ((t[i] - n[i])/t[i])*100 + "px"
    console.log(cats[i])
}