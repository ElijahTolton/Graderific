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

const sortableTable = document.querySelector("table.sortable");
if (sortableTable) {
    make_table_sortable(sortableTable);
}

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

const form = document.querySelector("form.formSubmit");
if(form){
    make_form_async(form);
}

async function make_form_async(form){

    // Add an eventListener
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const message = form.querySelector("span.message");
        try{
            message.innerText = "";
            const formData = new FormData(form);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const respone = await fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                },

            });
            if(!respone.ok){
                const text = await respone.text();
                message.innerText = "Upload failed:" + text;
            }else{
                // If the file loaded correctly reload the page.
                location.reload();
            }
            form.appendChild(message);

        }catch( error ){
            message.innerText = "Upload failed:" + error.message;
            form.appendChild(message);
        }
    });
}

if (sortableTable && document.getElementById("testGrade")) {
    make_grade_hypothesized(sortableTable);
}

function make_grade_hypothesized(table){
    const button = document.getElementById("testGrade");

    button.addEventListener("click", ()=>{
        const isHypothesized = table.id == "Hypothesized"

        // Switch toggle to other id value
        if(isHypothesized)
            table.id = "";
        else
            table.id = "Hypothesized";

        button.textContent = isHypothesized ? "Hypothesize" : "Actual grades" ;

        if(!isHypothesized){
            convertToInputs(table);
        } else{
            restoreGrades(table);
        }

        computeGrades(table);
    });
}

/**
 * Change all Not Due or Ungraded values in the table to input elements
 * @param {*} table 
 */
function convertToInputs(table){
    const rows = table.querySelectorAll("tbody tr");

    rows.forEach(row => {
        const gradeCell = row.querySelector(".grade");

        if (gradeCell && (gradeCell.textContent.trim() == "Not Due" || gradeCell.textContent.trim() == "Ungraded")){
            const originalText = gradeCell.textContent;
            const input = document.createElement("input");
            input.type = "number";
            input.min = 0;
            input.max = 100;
            input.placeholder = "";
            input.classList.add("hypotheticalInput");
            
            // Keep track of the origanl values to restore
            gradeCell.dataset.original = originalText;
            gradeCell.textContent = "";
            gradeCell.appendChild(input);

            input.addEventListener("keyup", ()=> computeGrades(table));
        }
    });
}

/**
 * Restore all grades to orignal Not Due or Ungraded.
 * @param {*} table 
 */
function restoreGrades(table){
    const input = table.querySelectorAll("input.hypotheticalInput");

    input.forEach(input =>{
        const cell = input.parentElement;
        const original = cell.dataset.original;
        cell.textContent = original;
        delete cell.dataset.original;
    });
}

/**
 * Compute grades everytime a keystroke is done in input box.
 * @param {*} table 
 */
function computeGrades(table){
    var totalWeight = 0;
    var totalPoints = 0;

    const rows = table.querySelectorAll("tbody tr");
    rows.forEach(row => {
        const gradeCell = row.querySelector(".grade");
        const weight = parseFloat(gradeCell.dataset.weight);
        var score;

        if(table.id == "Hypothesized"){
            const input = gradeCell.querySelector("input");
            if(input){
                score = parseFloat(input.value);
            }else if(gradeCell.textContent == "Missing"){
                score = 0;
            } else{
                score = parseFloat(gradeCell.dataset.value);
            }
        }else{
            const value = gradeCell.textContent.trim();
            try{
                if(value == "Missing"){
                    score = 0;
                }
                else{
                    score = parseFloat(value);
                }
            }catch (error){
                score = 0;
            }
        }

        if( !isNaN(score)){
            totalPoints += (score * (weight / 100));
            totalWeight += weight;
        }
    });

    const finalGrade = (totalPoints / totalWeight) * 100
    const finalGradeStr = Number(finalGrade.toFixed(1));
    const finalGradeCell = document.getElementById("finalGrade");

    if(finalGradeCell){
        finalGradeCell.textContent = finalGradeStr + "%";
    }
}

