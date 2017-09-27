var Footnotes = Footnotes || {};

var Footnotes = {

    counter: 1,

    increment: function() {
        $('.source-footnote-counter').each(function() {
            $(this).html(Footnotes.counter);
            Footnotes.counter ++;
        });
    },

    initPopovers: function() {
        $('[data-toggle="popover"]').popover({
            placement: 'top',
            html: true
        });
    }
};
