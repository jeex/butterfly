let textarea_to_iframe = function(){
    var val = $('textarea').val()
    val = val.replaceAll('href="#', 'href="about:srcdoc#');
    val = val.replaceAll('static/', 'https://cpnits.com/static/');
    $( 'iframe' ).attr( 'srcdoc', val);
}

$(function(){
    $('a.refresh-global-view').on('click', function(e){
        $( 'iframe' ).attr( 'src', function ( i, val ) { return val; });
    })

    $('a.refresh-local-view').on('click', function(e){
        textarea_to_iframe();
    })

    if($('a.refresh-local-view').length > 0){
        textarea_to_iframe();
    }

    // tab key in text area
    $('textarea').on('keydown', function(e){
        if(e.key == 'Tab'){
            e.preventDefault();
            var start = this.selectionStart;
            var end = this.selectionEnd;
            // set textarea value to: text before caret + tab + text after caret
            this.value = this.value.substring(0, start) + "\t" + this.value.substring(end);
            // put caret at right position again
            this.selectionStart = this.selectionEnd = start + 1;
        }
    });
})
