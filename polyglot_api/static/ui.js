"use strict";

$('.custom-file-input').on('change', function() {
    let fileNames = Array.from(this.files).map(f => f.name);
    $(this).next('.custom-file-label').text(fileNames.join(', '));
});
