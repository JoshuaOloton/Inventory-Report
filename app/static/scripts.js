// document.saddEventListener("click", testFunction)

function myFunction() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("myTable");
    tr = table.getElementsByTagName("tr");
  
    // Loop through all table rows, and hide those who don't match the search query
    for (i = 1; i < tr.length; i++) {
      td = tr[i].getElementsByTagName("td")[0]; // index 0 SEARCHES the ITEMS columns
      if (td) {
        txtValue = td.textContent || td.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
        } else {
          tr[i].style.display = "none";
        }
      }
    }
  }

  function testFunction() {
    // Declare variables
    var table, tr;
    table = document.getElementById("test");
    tr = table.getElementsByTagName("tr");
  
    console.log(tr.length);
    // Loop through all table rows, and hide those who don't match the search query
    for (let j = 1; j < tr.length; j++) {
      tr[j].style.display = "none";
    }
  }

  function testFunction() {
    alert("Page is loaded");
    var table, tr;
    table = document.getElementById("test");
    tr = table.getElementsByTagName("tr");
  
    console.log(tr.length);
    // Loop through all table rows, and hide those who don't match the search query
    for (let i = 1; i < tr.length; i++) {
      if (i > 5)
      {
        tr[i].style.display = "none";
      }
    }
  }