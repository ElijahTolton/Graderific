function say_hi(elt) {
    console.log("Welcome to", elt.innerText);
}

say_hi(document.querySelector("h1"));

function make_table_sortable(table){
    const headers = table.querySelectorAll("th.sort-column");
    const body = table.querySelector("tbody");

    // Add Event Listener for each sortable column in a sortable table.
    headers.forEach(header =>{
        // Add an event listener to each header when clicked reset all other
        // headers class names to be unsorted.
        header.addEventListener("click", (event)=>{
            const columnIndex = event.target.cellIndex;

            headers.forEach(h => {
                if( h !== header) h.className = "sort-column";
            });
            sortAscOrDesc(header, body, columnIndex);
        });
    });
}

make_table_sortable(document.querySelector("table.sortable"));

/**
 * Reorders table data when the last header cell is clicked on.
 * @param {The last header of the table} lastHeaderCell 
 * @param {The body of the table} body 
 */
function sortAscOrDesc(headerCell, body, columnIndex){
    // Get all rows in the body
    const rows = Array.from(body.querySelectorAll("tr"));

    // Get the current state of the data.
    const isDesc = headerCell.className == "sort-desc";
    const isAsc = headerCell.className == "sort-asc";
    const isUnsorted = headerCell.className == "sort-column";

    // Sort according graded or scores. If no numeric value do not sort.
    // If unsorted -> ascending order, ascending->descending
    if(isAsc || isUnsorted){
        rows.sort((row1, row2) =>{
            var value1 = row1.querySelector("td:nth-child(" + (columnIndex + 1) + ")").getAttribute("data-value");
            var value2 = row2.querySelector("td:nth-child(" + (columnIndex + 1) + ")").getAttribute("data-value");
    
            value1 = parseData(value1);
            value2 = parseData(value2);
    
            if(isNaN(value1) || isNaN(value2)){
                return 0;
            }
    
            // compare the float score values
            const compare = value1 - value2;
    
            return isUnsorted ? compare : -compare;
        });
    }
    // Data must be sorted descending. Descending->Unsorted
    else{
        rows.sort((row1, row2) =>{
            return row1.getAttribute("data-index") - row2.getAttribute("data-index");
        });
    }
    
    // Update class name
    if(isUnsorted)
        headerCell.className = "sort-asc";
    else if(isAsc)
        headerCell.className = "sort-desc";
    else if(isDesc)
        headerCell.className = "sort-column";

    // Update rows in the DOM
    rows.forEach( row => body.appendChild(row));
}

/**
 * Helper function to parse table data to get in comparable form.
 * @param {*} tableDataText 
 * @returns A parsed float value.
 */
function parseData(tableDataText){    
    // If admin view parse the fraction that is being displayed.
    if (tableDataText.includes("/")) {
        const [numerator, denominator] = tableDataText.split("/").map(str => parseFloat(str.trim()));
        if (!isNaN(numerator) && !isNaN(denominator) && denominator !== 0) {
            return (numerator / denominator);
        }
    }
    else{
        // If not fraction use just parse the numbers
        return parseFloat(tableDataText);
    }
}