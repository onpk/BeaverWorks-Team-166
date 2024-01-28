const cats = ["School", "Summer", "Friends", "Sports", "Sarcasm", "Texting", "Pets", "Theater"];
const n = [8, 3, 2, 4, 3, 2, 12, 17];
const t = [20, 5, 3, 6, 3, 3, 20, 20];

for (let i = 0; i < cats.length; i++) {
    document.getElementById("i" + (i+1).toString()).textContent=cats[i].concat(" (", n[i].toString(), ")");
    var pn = document.getElementById("p" + (i+1).toString());
    pn.style.width = ((t[i] - n[i])/t[i])*100 + "px"
    console.log(cats[i])
}