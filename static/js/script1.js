<script>
function chooseDeck(deck) 
{
  fetch("/choose_deck", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ deck: deck })
  })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert(data.error);
      } else if (data.finished) {
        window.location.href = "/final";
      } else {
        sessionStorage.setItem("gain", data.gain);
        sessionStorage.setItem("penalty", data.penalty);
        sessionStorage.setItem("net_gain", data.net_gain);
        sessionStorage.setItem("round", data.round);
        window.location.href = "/gain_loss";
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Something went wrong! Check console."); 
    })
}

</script>
