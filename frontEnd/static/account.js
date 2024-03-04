import * as fs from "fs";

const fs = require("fs");

const form = document.querySelector("form");
form.addEventListener("submit", (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const obj = Object.fromEntries(fd);
    console.log(obj);

    const json = JSON.stringify(obj);
    fs.writeFile("interests.json", json, (error) => {
        if (error) {
            console.error(error);
        }
        throw error;
    })
    console.log("data written");
})