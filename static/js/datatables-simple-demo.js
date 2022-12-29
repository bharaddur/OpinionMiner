window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki
  
    const datatablesSimple = document.getElementById('datatablesSimple');
    if (datatablesSimple) {
      new simpleDatatables.DataTable(datatablesSimple, {
        select: {
          style: 'single' // enable single row selection
        },
        buttons: ['csv'] // add a button to export the table data to a CSV file
      });
    }
  });
  