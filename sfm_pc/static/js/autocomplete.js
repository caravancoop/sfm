$(document).on("keydown.autocomplete", ".autocomplete-tag", function() {
    self = this;
    $(this).autocomplete({
        source: "/" + window.LANG + $(this).data('source-url'),
        select: function(event, ui) {
            event.preventDefault();
            $(self).val(ui.item.label);
            input_id = $(self).data('id');
            $(self).parent().find('#' + input_id).val(ui.item.value);
        }
    });
});
