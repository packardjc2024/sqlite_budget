window.onload = setTimeout(check_remaining, 500);

document.addEventListener('DOMContentLoaded', function(){
    document.getElementById('change_month').addEventListener('change', change_month);
    var table = document.getElementById('expenses_table');
    for (var i = 0; i < table.rows.length; i++){
        table.rows[i].addEventListener('click', select_row);
    }
});


function check_remaining(){
    const low = 50;
    if (window.location.pathname == '/budget/'){
        amounts = document.getElementsByClassName('remaining-budget');
        headers = document.getElementsByClassName('budget-header');
        for (var i = 0; i < amounts.length; i++){
            if (parseFloat(amounts[i].innerHTML) < 0){
                alert(`WARNING! \n ${headers[i].innerHTML} is ${amounts[i].innerHTML}`);
            } else if (parseFloat(amounts[i].innerHTML) < low){
                alert(`WARNING! \n ${headers[i].innerHTML} has less than ${low} remaining`)
            }
        }
    }
}

function change_month(){
    let element = document.getElementById('change_month')
    let budget = element.value;
    let month = element.options[this.selectedIndex].text;
    window.location.replace(`/budget/change_month/${month}`);
}

let selected_row = null;

function select_row(){
    if (selected_row === this){
        this.style.backgroundColor = 'white';
        selected_row = null;
    } else {
        if (selected_row){
        selected_row.style.backgroundColor = "white";
        }
        this.style.backgroundColor = "red";
        let expense_id = this.cells[0].innerHTML;
        selected_row = this;
        showOptions(expense_id, this);
    }
}

function showOptions(expense_id){
    let popup = document.getElementById('popup');
    popup.className = 'popup';
    document.getElementById('popup_text').innerHTML = `What would you like to do with expense ${expense_id}?`;
    document.getElementById('delete_form').action = `/budget/delete_expense/${expense_id}/`;
    document.getElementById('edit_form').action = `/budget/edit_expense/${expense_id}/`;
}


function disable_month(){
    // if (window.location.pathname == test('/budget/edit_budget/.*')){
    if (window.location.pathname == '/budget/edit_budget/'){
        month = document.getElementById('id_budget_month');
        month.readOnly = true;

    }
}