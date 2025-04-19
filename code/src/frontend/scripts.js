async function fetchSuggestions(query, index) {
    if (query.length < 3) return;
    const response = await fetch(`/search?query=${query}`);
    const results = await response.json();
    
    const suggestionsDiv = document.getElementById(`suggestions${index}`);
    suggestionsDiv.innerHTML = "";
    suggestionsDiv.style.display = results.length > 0 ? "block" : "none";
    
    results.forEach(game => {
        let div = document.createElement("div");
        div.className = "suggestion-item";
        div.innerHTML = `<img src="${game.image}" width="40"> ${game.name}`;
        
        div.onclick = () => {
            document.getElementById(`game${index}`).value = game.name;
            suggestionsDiv.innerHTML = "";
            suggestionsDiv.style.display = "none";
            changeBackgroundImage(game.image, index);
        };
        suggestionsDiv.appendChild(div);
    });
}

function changeBackgroundImage(imageUrl, sectionIndex) {
    const section = document.getElementById(`section${sectionIndex}`);
    section.style.backgroundImage = `url(${imageUrl})`;
}

document.querySelectorAll(".game-input").forEach((input, index) => {
    input.addEventListener("input", () => fetchSuggestions(input.value, index + 1));
});

document.getElementById("recommendBtn").addEventListener("click", async () => {
    const games = [
        document.getElementById("game1").value,
        document.getElementById("game2").value,
        document.getElementById("game3").value
    ].filter(game => game.trim() !== "");  // Remove empty inputs

    if (games.length === 0) {
        alert("Please enter at least one game.");
        return;
    }

    const response = await fetch("/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ games })
    });

    if (response.ok) {
        window.location.href = "/recommend";  // Redirect to the recommendations page
    } else {
        alert("Error fetching recommendations.");
    }
});

function revealInput(index) {
    const placeholder = document.getElementById(`placeholder${index}`);
    const inputGroup = document.getElementById(`inputGroup${index}`);

    if (placeholder.style.display !== "none") {
        placeholder.style.display = "none";
        inputGroup.style.display = "flex";
    }
}