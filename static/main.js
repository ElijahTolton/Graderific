function say_hi(elt) {
    console.log("Welcome to", elt.innerText);
}

say_hi(document.querySelector("h1"));

function make_table_sortable(table){
    
    console.log(table);
    const lastHeaderCell = table.querySelector("thead tr th:last-child");
    const body = table.querySelector("tbody");
    console.log(lastHeaderCell);

    lastHeaderCell.addEventListener("click", function() {
        sortAscOrDesc(lastHeaderCell, body);
    });
}

make_table_sortable(document.querySelector("table"));

/**
 * Reorders table data when the last header cell is clicked on.
 * @param {The last header of the table} lastHeaderCell 
 * @param {The body of the table} body 
 */
function sortAscOrDesc(lastHeaderCell, body){
    // Get all rows in the body
    const rows = Array.from(body.querySelectorAll("tr"));

    // get what sorting order it is.
    const isAscending = lastHeaderCell.className == "sortable" || lastHeaderCell.className == "sort-desc";

    // Sort according graded or scores. If no numeric value do not sort.
    rows.sort((row1, row2) =>{
        var value1 = row1.querySelector("td:last-child").innerText;
        var value2 = row2.querySelector("td:last-child").innerText;

        value1 = parseData(value1);
        value2 = parseData(value2);

        if(isNaN(value1) || isNaN(value2)){
            return 0;
        }

        // compare the float score values
        const compare = value1 - value2;

        return isAscending ? compare : -compare;
    });

    // Update class name
    lastHeaderCell.className = isAscending ? "sort-asc" : "sort-desc";

    rows.forEach( row => body.appendChild(row))
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