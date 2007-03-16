$(function() {
$.datePicker.setDateFormat('<?cs var:datefield.format ?>','<?cs var:datefield.sep ?>');
<?cs each:id = datefield.ids ?>
$('#<?cs var:id ?>').datePicker();
<?cs /each ?>
$('a.date-picker').css('background', 'url(<?cs var:datefield.calendar ?>) no-repeat')
});