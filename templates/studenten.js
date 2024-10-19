var filters = {}; // column:[value]

let isValidHttpUrl = function(string){
    let url;
    try{
        url = new URL(string);
    }catch (_){
        return false;
    }
    return url.protocol === "http:" || url.protocol === "https:";
}

let filters_count_shown = function(){
    var shown = 0
    $.each($('tbody tr'), function(){
        if($(this).is(":visible")){
            shown++;
        }
    });
    return shown;
}

let filters2string = function(){
    var eruit = ''
    for(key in filters){
        eruit += '<strong>'+key+'</strong> = '+filters[key].toString()+'<br>'
    }
    return eruit.replaceAll(',', ', ');
}

let add_2_filter = function(td_o, empty) {
    let key = td_o.attr('data-th');
    if(td_o.attr('id') == '') {
        // checkbox, ignore
        return;
    }
    if(empty){
        filters = {}
    }
    if (filters.hasOwnProperty(key)) {
        if (!filters[key].includes(td_o.text())) {
            filters[key].push(td_o.text())
        }
    } else {
        filters[key] = [td_o.text()]
    }
}

let filteren = function(){
    $('tbody tr').hide();
    $('tbody td').removeClass('filteredcel')
    $.each($('tbody tr'), function(){
        let rij = $(this);
        var tonen = true;
        for(var key in filters){
            // ignore checkbox value
            if(key == 'checked'){
                continue;
            }
            let cel = rij.find('td[data-th="'+key+'"]'); // cel met te filteren kolom
            if(filters[key].includes(cel.text())){
                cel.addClass('filteredcel')
            }else{
                tonen = tonen && false;
            }
        }
        if(tonen){
            rij.show();
        }
    });
    $('td input[type="checkbox"]:checked').parent().parent().show();
}

let sortTable = function(td_nr, order) {
    let table = $('table')
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

let tabel2csv = function(header) {
    // Select rows from table_id
    var csvtext = '';
    if (header) {
        var eerste = true;
        var komma = '';
        $.each($('thead th'), function () {
            if (eerste) {
                // skip checkbox field
                eerste = false;
            } else {
                $(this).find('span').html(''); // pijltje eruit
                csvtext += komma + $(this).text();
                komma = ';';
            }
        });
        csvtext += "\n";
    }

    var nietnul = false;
    $.each($('tbody tr'), function () {
        let rij = $(this);
        let checked = $(this).find('td input[name="add"]').prop('checked');
        if (rij.is(":visible") && checked) {
            var eerste = true;
            komma = '';
            $.each(rij.find('td'), function () {
                if (eerste) {
                    // skip checkbox field
                    eerste = false;
                } else {
                    nietnul = true;
                    let t = $(this).data('csv');
                    if($(this).hasClass('circular')){
                        console.log($(this).data('cirval'))
                        if(t === 0){
                            csvtext += komma + '';
                        }else if(t === 1){
                            csvtext += komma + 'green';
                        }else if(t === 2){
                            csvtext += komma + 'orange';
                        }else if(t === 3){
                            csvtext += komma + 'red';
                        }
                    }else{
                        csvtext += komma + t;
                    }
                    komma = ';';
                }
            })
            csvtext += "\n";
        }
    });
    if(nietnul){
        $('#csv-area').val(csvtext);
        return true;
    }else{
        return false;
    }
}
/* off because handled by a request.
let download_excel = function(){
    let csvtext = $('#csv-area').val().trim();
    if(csvtext === ''){
        return;
    }
    var encodedUri = encodeURI(csvtext);
    var link = document.createElement("a");
    link.setAttribute("href", "data:text/csv;charset=utf-8,\uFEFF" + encodedUri);
    link.setAttribute("download","report.csv");
    link.click();
}
*/
let click_to_group = function(){
    // maakt groep-vak rechtsklik-baar als student actief.
    let acts = {{ actiefstats|safe }}
    $.each($('tbody tr'), function(){
        let status = $(this).attr('data-status')*1;
        let filter = $(this).attr('data-filter');
        if(acts.includes(status) || true) {
            $(this).find('td[data-th="s_group"]')
                .on('contextmenu', function (e) {
                    e.preventDefault();
                    window.location.replace('/groepen/' + $(this).attr('data-idnr'));
                });
        }else{
            $(this).find('td')
                .on('contextmenu', function (e) {
                    e.preventDefault();
                });
        }
    })
}

let get_checked_ids = function(){
    var lijst = [];
    $('td input[name="add"]:checked').each(function(){
        lijst.push($(this).val()*1);
    });
    return lijst;
}

let checked_emails = function(){
    var csv = ''
    $('td input[name="add"]:checked').closest('tr').each(function(){
        let id = $(this).attr('id') * 1;
        let em = $(this).find('td[data-th="email"]').text();
        csv += em + '\r\n';
    });
    $('#csv-area').val(csv);
}

let collectief_verzenden = function(){
    let lijst = get_checked_ids();
    if(lijst.length == 0){
        return false;
    }
    $('input[name="col-ids"]').val(lijst);

    let s_group = $('select[name="to-group"]').find(":selected").val();
    let s_status = $('select[name="to-status"]').find(":selected").val();
    if(s_group == 0 && s_status == 0){
        return false;
    }
    // verzenden
    return true;
}

$(function(){
    $('button[name="tocsv"]').on('click', function(){
        tabel2excel();
    })

    // sort on column
    $('table th:not(.no-sort)').on('click', function(){
        let th = $(this);
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
                sortTable(i, richting)
            }
        });
        $('th span').html('');
        if(richting == 'asc'){
            th.find('span').html('&darr;');
        }else{
            th.find('span').html('&uarr;');
        }
        $('#no-ajax input[name="sort-field"]' ).val(th.attr('id'));
        $('#no-ajax input[name="sort-dir"]' ).val(richting);
        $('#asshole input[name="sort-field"]' ).val(th.attr('id'));
        $('#asshole input[name="sort-dir"]' ).val(richting);
        let all_aas = $('a.must-sort');
        $.each(all_aas, function(k, v){
            var href = $(this).attr('href');
            href = href.split('?')[0];
            href = href+'?sort-field='+th.attr('id')+'&sort-dir='+richting;
            $(this).attr('href', href);
        })
    });

    // checkboxes on and off
    $('th input[type="checkbox"]').on('change', function(){
        if($(this).is(':checked')){
            $('tr:visible td input[type="checkbox"]').prop('checked', true);
        }else{
            $('tr:visible td input[type="checkbox"]').prop('checked', false);
        }
    })

    // show-hide on cel value
    $('table td:not(.dblignore)').on('dblclick', function(){
        let td_o = $(this)
        // https://craftpip.github.io/jquery-confirm/
        $.confirm({
            columnClass: 'medium',
            containerFluid: true,
            title: 'Filters ['+filters_count_shown()+'] :',
            content: filters2string(),
            autoClose: 'cancel|8000',
            buttons: {
                cancel: {
                    text: 'Annuleer',
                    btnClass: 'btn-white',
                    keys: ['esc'],
                    action: function(){
                        // niets doen
                    }
                },
                reset_filter: {
                    text: 'Reset',
                    btnClass: 'btn-red',
                    keys: [],
                    action: function(){
                        filters = {}
                        $('tbody td').removeClass('filteredcel')
                        $('tbody tr').show();
                    }
                },
                new_filter: {
                    text: 'Nieuw & Go',
                    btnClass: 'btn-blue',
                    keys: [],
                    action: function(){
                        add_2_filter(td_o, true);
                        filteren();
                    }
                },
                add_to_filter: {
                    text: 'Voeg toe',
                    btnClass: 'btn-orange',
                    keys: [],
                    action: function(){
                        add_2_filter(td_o, false)
                    }
                },
                add_to_go_filter: {
                    text: 'Voeg toe & Go',
                    btnClass: 'btn-blue',
                    keys: ['enter'],
                    action: function(){
                        add_2_filter(td_o, false)
                        filteren();
                    }
                },
                go_filter: {
                    text: 'Go',
                    btnClass: 'btn-blue',
                    keys: ['enter'],
                    action: function(){
                        filteren();
                    }
                }
            },
            onDestroy: function(){
                // niets
            },
        });
    })

    // disable context menu on tables
    $('td, th')
        .on('contextmenu', function(e){
            e.preventDefault();
        })

    // contrasteren tekst in cellen en .contrast class
    $('td, .contrast')
        .each(function(){
            let kleur = $(this).css('background-color');
            let contra = calc_contra_color(kleur)
            $(this).css('color', contra);
        });

    // als op collectief geklikt
    $('form[name="to-collectief"]').on('submit', function(e){
        // alle aangevinkte id's naar veld col-ids
        if(! collectief_verzenden()){
            e.preventDefault();
        }
    });

    $('input[name="to-emails"]').on('click', function(e){
        e.preventDefault();
        checked_emails();
    })
    $('input[name="to-csv"]').on('click', function(e) {
        e.preventDefault();
        tabel2csv(header=true)
    });

    $('input[name="to-excel"]').on('click', function(e) {
        if( tabel2csv(header=true) ){
            // submit form
        }else{
            e.preventDefault();
        }
        // download_excel();
    });

    // sort at start
    {% if filter == 'registratie' %}
        $('table th:nth-of-type(2)').trigger('click').trigger('click')
    {% elif filter == 'studenten' %}
        $('table th:nth-of-type(3)').trigger('click')
    {% elif filter == 'beoordelen' %}
        $('table th:nth-of-type(3)').trigger('click')
    {% elif filter == 'alumni' %}
        $('table th:nth-of-type(4)').trigger('click')
     {% elif filter == 'niet' %}
       $('table th:nth-of-type(4)').trigger('click')
    {% elif filter == 'noshow' %}
        $('table th:nth-of-type(4)').trigger('click')
    {% else %}
        // als for groups
        const urlParams = new URLSearchParams(window.location.search);
        const sortfield = urlParams.get('sort-field');
        const sortdir = urlParams.get('sort-dir');
        if(sortfield && sortdir){
            if(sortdir === 'asc'){
                $('table th#'+sortfield).trigger('click');
            }else{
                $('table th#'+sortfield).trigger('click');
                $('table th#'+sortfield).trigger('click');
            }
        }else{
            {% if 'views' in request.url %}
                $('table th:nth-of-type(5)').trigger('click')
            {% else %}
                $('table th:nth-of-type(4)').trigger('click')
            {% endif %}
        }
    {% endif %}

    $('#csv-area').css('width', $('table').width());

    click_to_group();
});