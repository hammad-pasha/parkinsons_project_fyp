$(document).on('click', '.chat-ai', function() {
    $('.chat-ai').hide();
    $('.ai_side_panel').toggleClass('AIpanel-visible');
});

$(document).on('click', '#ai_side_close', function() {
    $('.ai_side_panel').toggleClass('AIpanel-visible');
    $('.chat-ai').show();
});

$(document).on('click', '#ai_side_panel #send', function() {
    var message = $('#ai_side_panel #message').val();
    if (message == '') return;
    $('#ai_side_panel #message').val('');
    $('#ai_side_panel .chatMessages').append(`
        <div class="message mMess">
            <div class="prof" style="background-color: #1977cc;">
                <p>C</p>
            </div>
            <div class="messArea">
                <p class="sname">Human</p>
                <div class="ai_textM bg-light shadow">${message}</div>
            </div>
        </div>
    `);
    var data = {
        'question': message
    };
    $('#ai_side_panel .content_loader').show();
    axios.post("https://4whfmugx96.execute-api.us-east-1.amazonaws.com/ParkinsonChat", 
        JSON.stringify(data),
        { headers: { 'Content-Type': 'application/json' } }
    ).then((response) => {
        console.log(response);
        $('#ai_side_panel .content_loader').hide();
        $('#ai_side_panel .chatMessages').append(`
            <div class="message mMess">
                <div class="prof" style="background-color: #1977cc;">
                    <p>AI</p>
                </div>
                <div class="messArea">
                    <p class="sname">AI Bot</p>
                    <div class="ai_textM shadow">${response.data}</div>
                </div>
            </div>
        `);
    })
});