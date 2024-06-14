
let calc_contra_color = function(kleur){
    if(kleur)
    // Variables for red, green, blue values
    var r, g, b, hsp;
    // Check the format of the color, HEX or RGB?
    if (kleur.match(/^rgb/)) {
        // If RGB --> store the red, green, blue values in separate variables
        kleur = kleur.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+(?:\.\d+)?))?\)$/);
        r = kleur[1];
        g = kleur[2];
        b = kleur[3];
    }
    else {
        // If hex --> Convert it to RGB: http://gist.github.com/983661
        kleur = +("0x" + kleur.slice(1).replace(
        kleur.length < 5 && /./g, '$&$&'));
        r = kleur >> 16;
        g = kleur >> 8 & 255;
        b = kleur & 255;
    }
    // HSP (Highly Sensitive Poo) equation from http://alienryderflex.com/hsp.html
    hsp = Math.sqrt(
    0.299 * (r * r) +
    0.587 * (g * g) +
    0.114 * (b * b)
    );
    // Using the HSP value, determine whether the color is light or dark
    if (hsp>127.5) {
        return 'black';
    }
    else {
        return 'white';
    }
}

