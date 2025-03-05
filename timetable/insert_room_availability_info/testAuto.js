fetch("http://localhost:5000/fetch_and_update_schedule")
  .then(response => response.json())
  .then(data => {
    console.log(data.message);
  })
  .catch(error => console.error("Error:", error));
