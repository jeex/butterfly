let newid = function(){
    // activate by click in id field
    var hoger = 0;
    $.each($('tbody tr td:first-child'), function(){
        let nr = $(this).text() * 1;
        if(isNaN(nr)){
            hoger = '';
            return hoger;
        }else {
            nr = nr * 1;
            hoger = Math.max(hoger, nr) + 1;
        }
    })
    return hoger;
}

let sortTable = function(table, td_nr, order) {
    let asc = order === 'asc';
    let tbody = table.find('tbody');
    tbody.find('tr').sort(function(a, b) {
        if (asc) {
            return $('td:nth-child('+td_nr+')', a).text().localeCompare($('td:nth-child('+td_nr+')', b).text());
        } else {
            return $('td:nth-child('+td_nr+')', b).text().localeCompare($('td:nth-child('+td_nr+')', a).text());
        }
    }).appendTo(tbody);
}

let sortClick = function(deze){
    let th = $(deze);
        var i = 0;
        var richting = 'asc';
        $.each($('table th'), function(k, v){
            i++;
            if($(this).attr('id') == th.attr('id')){
                // get asc/desc
                if($(this).find('span').text() == String.fromCharCode(8593)){
                    // was up, goes down
                    richting = 'asc';
                }else if($(this).find('span').text() == String.fromCharCode(8595)){
                    // was down, goes up
                    richting = 'desc';
                }
                sortTable($('table'), i, richting)
            }
        });
        $('th span').html('');
        if(richting == 'asc'){
            th.find('span').html('&darr;');
        }else{
            th.find('span').html('&uarr;');
        }
}

/*
let rowClick = function(deze){
    let rij = $(deze);
    // velden in form invullen. Volgorde is zelfde in form als in row
    $.each($(rij).find('td'), function(key, val){
        let td = $(val)
        let tdval = td.text();
        let th = $('thead th:nth-child('+(key+1)+')').attr('id');
        if(th == 'status') {
            if (tdval == 'active') {
                tdvalnr = 1;
            } else {
                tdvalnr = 0;
            }
            $('form input[name="status"][value="' + tdvalnr + '"]').prop('checked', true);
        }else if(th == 'color' && tdval == ''){
            tdval = '#ffffff';
        }else{
            $('form input[name="'+th+'"]').val(tdval);
        }
    })
    $('input[type="submit"]').removeClass('verborgen');
    $('html, body').animate({
        scrollTop: 0
    }, 100);
}
*/
let wireReorderList = function(){
    $("#reorderExampleItems").sortable();
    $("#reorderExampleItems").disableSelection();
}

let saveOrdering = function(){
    var ordering = [] // ordering of id's
    $.each($('table tbody.sort tr'), function(){
        ordering.push($(this).attr('data-id')*1);
    });
    console.log(ordering)
    $('form[name="order"] input[name="ordering"]').val(ordering)
    return true;
}

$(function(){
   // sort on column
    $('table th').on('click', function(){
        sortClick(this);
    });

    /*  // click on tbody td
    $('table tbody tr').on('click', function(){
       rowClick(this)
    });
    */

    // save form
    $('form[name="edit"]').on('submit', function(e){
        let knop = $(this).find("input[type=submit]:focus").val();
        if($('form input[name="id"]').val() == ''){
            e.preventDefault();
            return;
        }
    });

    $('td.kleur').each(function(){
        let bgc = $(this).css('background-color');
        let contra = calc_contra_color(bgc);
        $(this).css('color', contra);
    });

    // click in empty id field
    $('button.new').on('click', function(e){
        e.preventDefault();
        $('input[name="id"]').val(newid());
        $('input[name="name"]').val('');
        $('input[name="color"]').val('#ffffff');
        $('input[name="extra"]').val('');
        $('input[name="ordering"]').val(0);
        $('input[name="status"][value="1"]').prop('checked', true);
        $('input[type="submit"]').removeClass('verborgen');
        $('input[type="submit"][value="Delete"]').addClass('verborgen');
    });
    if(id > 0){
        $('table tr[data-id="'+id+'"]').trigger('click');
    }
    $('.sort').sortable({
        cursor: 'move',
        axis: 'y',
        update: function(e, ui) {
            $(this).sortable('refresh');
        }
    });
    $('form[name="order"]').on('submit', function(e){
        if(saveOrdering()){
            // ok
        }else{
            e.preventDefault();
        }
    });
    wireReorderList();
});