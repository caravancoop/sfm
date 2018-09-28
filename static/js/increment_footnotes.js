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
            placement: 'auto',
            html: true,
            content: function(popover){

            }
        });
         $('[data-toggle="tooltip"]').tooltip();

        // Show footnotes on hover
        $('.citation-container, .cited').on('mouseover', function() {
            $(this).find('.citation').css('visibility', 'visible');
        })

        $('.citation-container, .cited').on('mouseout', function() {
            // Hide the citation if a popover is not visible
            if ($(this).has('.popover').length === 0) {
                $(this).find('.citation').css('visibility', 'hidden');
            }
        })

        $(document).on('click', function (e) {
            $('[data-toggle="popover"],[data-original-title]').each(function () {
                // Thanks to Matt Lockyer for this great solution to allow
                // popovers to be closed when the user clicks elsewhere

                //the 'is' for buttons that trigger popups
                //the 'has' for icons within a button that triggers a popup
                if (!$(this).is(e.target) && $(this).has(e.target).length === 0
                    && $('.popover').has(e.target).length === 0) {
                    (($(this).popover('hide').data('bs.popover') ||
                      {}).inState ||
                        {}).click = false; // fix for BS 3.3.6
                    $(this).parents('.citation').css('visibility', 'hidden');
                }
            });
        });

        $(document).on('shown.bs.popover', function(e) {

            // Init dismiss buttons
            var params = {'object_info': $(e.target).data('object_info')};
            var citation_url = $(e.target).data('citation_url');
            var popover = $(e.target).data('bs.popover');
            $.when($.get(citation_url, params)).then(function(response){
                $(e.target).attr('data-content', response);
                popover.setContent();
                $('[data-dismiss="popover"]').click(function() {
                    (($(this).parents('.popover').popover('hide').data('bs.popover') ||
                    {}).inState ||
                        {}).click = false;  // fix for BS 3.3.6
                    $(this).parents('.citation').css('visibility', 'hidden');
                });
            })
        });

    }
};
