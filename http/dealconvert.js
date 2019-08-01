$(document).ready(function() {
    $('a.faq-btn').popover();
    $('input[name="output"]').change(function() {
        if ($('input[name="output"]:checked').length > 0) {
            $('#submit-btn').removeAttr('disabled');
            if ($('input[name="output"][value="pbn"]').is(':checked')) {
                $('#analyze-boards').removeAttr('disabled');
            } else {
                $('#analyze-boards').attr('disabled', 'disabled').prop('checked', false);
            }
        } else {
            $('#submit-btn').attr('disabled', 'disabled');
            $('#analyze-boards').attr('disabled', 'disabled').prop('checked', false);
        }
    });
    $('#input-files').change(function() {
        $('#submit-panel, #output-formats').collapse(this.files.length ? 'show' : 'hide');
    });
    $('#converter-input').submit(function() {
        var that = $(this);
        var output = [];
        that.find('input[name="output"]:checked').each(function() {
            output.push(this.value);
        });
        var display = that.find('input[name="display"]').is(':checked');
        var analyze = that.find('input[name="analyze"]').is(':checked');
        var files = {};
        var formFiles = this['input-files'].files;
        if (formFiles.length) {
            $('.output-group').remove();
            that.css('opacity', 0.3);
            that.find('input, button').attr('disabled', 'disabled');
        }
        var completed = 0;
        for (var i = 0; i < formFiles.length; i++) {
            var currentFile = formFiles[i];
            files[currentFile.name] = null;
            var reader = new FileReader();
            reader.file = currentFile;
            reader.onload = function(e) {
                files[e.target.file.name] = btoa(e.target.result);
                for (var file in files) {
                    if (files[file] == null) {
                        return;
                    }
                }
                for (var file in files) {
                    var paramObj = {
                        'name': file,
                        'content': files[file],
                        'output': output,
                        'display_deals': display,
                        'analyze_deals': analyze
                    };
                    $.ajax(
                        'api/upload/',
                        {
                            data: JSON.stringify(paramObj),
                            dataType: 'json',
                            method: 'POST',
                            success: function(data, status, xhr) {
                                var outputGroup = $('template#file-output-group').clone().contents().unwrap();
                                var warningTemplate = $('template#file-output-warning');
                                var errorTemplate = $('template#file-output-error');
                                var fileTemplate = $('template#file-output');
                                var inputHeader = outputGroup.find('.file-header');
                                inputHeader.text(data.name);
                                var groupBody = outputGroup.find('.file-body');
                                if (data.error) {
                                    inputHeader.addClass('bg-danger');
                                    groupBody.append(errorTemplate.clone().contents().unwrap().text(data.error));
                                } else {
                                    inputHeader.addClass('bg-success');
                                    if (data.warnings.length) {
                                        inputHeader.removeClass('bg-success');
                                        inputHeader.addClass('bg-warning');
                                        for (var w = 0; w < data.warnings.length; w++) {
                                            groupBody.append(warningTemplate.clone().contents().unwrap().text(data.warnings[w]));
                                        }
                                    }
                                    for (var f = 0; f < data.files.length; f++) {
                                        var fileContent = fileTemplate.clone().contents().unwrap();
                                        groupBody.append(fileContent);
                                        fileContent.find('.file-name').text(data.files[f].name);
                                        fileContent.find('.file-status').popover();
                                        if (data.files[f].error) {
                                            fileContent.find('.file-link').remove();
                                            fileContent.find('.file-status').addClass('btn-danger').text('⚠️').attr('data-content', data.files[f].error);
                                            fileContent.find('.file-name').addClass('btn-danger');
                                            inputHeader.removeClass('bg-success');
                                            inputHeader.addClass('bg-warning');
                                        } else {
                                            if (data.files[f].warnings.length) {
                                                fileContent.find('.file-status').addClass('btn-warning').text('⚠️').attr(
                                                    'data-content', data.files[f].warnings.join("<br />"));
                                                fileContent.find('.file-name').addClass('btn-warning');
                                                inputHeader.removeClass('bg-success');
                                                inputHeader.addClass('bg-warning');
                                            } else {
                                                fileContent.find('.file-status').addClass('btn-success').text('✔️');
                                                fileContent.find('.file-name').addClass('btn-success');
                                            }
                                            fileContent.find('.file-link').attr(
                                                'href', 'api/' + data.files[f].link
                                            );
                                        }
                                    }
                                    if (data.preview) {
                                        var boardTemplate = $('#board-preview');
                                        var hands = ['north', 'east', 'south', 'west'];
                                        var suits = ['spades', 'hearts', 'diamonds', 'clubs'];
                                        for (var b = 0; b < data.preview.length; b++) {
                                            var board = boardTemplate.clone().contents().unwrap();
                                            board.find('.board-number').text(data.preview[b].number);
                                            board.find('.board-conditions').attr('src', 'img/' + data.preview[b].conditions + '.png');
                                            for (var h = 0; h < hands.length; h++) {
                                                for (var s = 0; s < suits.length; s++) {
                                                    board.find('.board-' + hands[h] + '-' + suits[s]).text(data.preview[b].hands[h][s].join(''));
                                                }
                                            }
                                            outputGroup.find('.file-boards-panel .board-body').append(board);
                                        }
                                    } else {
                                        outputGroup.find('.file-boards-panel').remove();
                                    }
                                }
                                $('body').append(outputGroup);
                                completed += 1;
                                if (completed >= formFiles.length) {
                                    that.css('opacity', '');
                                    that.find('input, button').removeAttr('disabled');
                                }
                            },
                            error: function(xhr, status, error) {
                                var errorBox = $('<div class="container output-group"></div>');
                                errorBox.append($('template#file-output-error').clone().contents().unwrap().text(
                                    'Nie udało się wykonać konwersji: ' + xhr.responseText
                                ));
                                $('body').append(errorBox);
                                that.css('opacity', '');
                                that.find('input, button').removeAttr('disabled');
                            }
                        }
                    );
                }
            }
            reader.readAsBinaryString(currentFile);
        }
        return false;
    });
});
