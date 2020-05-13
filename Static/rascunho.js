function nome_cadastrado(nome){
    // console.log('Aqui é o nome' + nome)
    let contatos = $('h5.name')
    console.log(contatos)
    if(contatos.length > 0){
        for(c of contatos){
            console.log(c, c.innerText) 
            console.log('Eu encontrei' + c.innerText)
            let verifica = c.innerText == nome ? true : false
            // console.log(`O nome ${nome} não é igual a ${c.innerText}`)
            return verifica
        }
    }
    else{
        return false
    }
}
function add_contato(iter, new_msg){
    for(obj of iter['dados']){
        let nome = obj['contato']
        // console.log('DEBUG' + nome)
        let mensagem = obj['mensagem']
        console.log('Nome do contato: ' + nome)
        let verificador = nome_cadastrado(nome)
        // console.log(verificador)
        if(verificador == false){
            if(new_msg){
                $('.inbox_chat').prepend(
                  `<div class="chat_list">
                    <div class="chat_people">
                      <div class="chat_img"> <img src="https://ptetutorials.com/images/user-profile.png" alt="sunil"> </div>
                      <div class="chat_ib">
                        <h5 class='name'>${nome}</h5>
                        <p class='msg'>${mensagem}</p>
                      </div>
                    </div>
                  </div>`)
            }
            else{
              $('.inbox_chat').append(
                `<div class="chat_list">
                    <div class="chat_people">
                      <div class="chat_img"> <img src="https://ptetutorials.com/images/user-profile.png" alt="sunil"> </div>
                      <div class="chat_ib">
                        <h5 class='name'>${nome}</h5>
                        <p class='msg'>${mensagem}</p>
                      </div>
                    </div>
                  </div>`)
            }
            
        }
        else{
            return undefined
        }
    }
}

function debugando(iter, new_msg){
  for(obj of iter['dados']){
    let nome = obj['nome']
    let mensagem = obj['mensagem']
    let contatos_on_dom = $('h5.name')

    if(contatos_on_dom.length > 0){
      for(c of contatos_on_dom){
        if (c.innerText != nome){
          if(new_msg){
                $('.inbox_chat').prepend(
                  `<div class="chat_list">
                    <div class="chat_people">
                      <div class="chat_img"> <img src="https://ptetutorials.com/images/user-profile.png" alt="sunil"> </div>
                      <div class="chat_ib">
                        <h5 class='name'>${nome}</h5>
                        <p class='msg'>${mensagem}</p>
                      </div>
                    </div>
                  </div>`)
            }
            else{
              $('.inbox_chat').append(
                `<div class="chat_list">
                    <div class="chat_people">
                      <div class="chat_img"> <img src="https://ptetutorials.com/images/user-profile.png" alt="sunil"> </div>
                      <div class="chat_ib">
                        <h5 class='name'>${nome}</h5>
                        <p class='msg'>${mensagem}</p>
                      </div>
                    </div>
                  </div>`)
            }
        }
        else{
          console.log('!')
        }
      }
    }
    else{
      $('.inbox_chat').append(
                `<div class="chat_list">
                    <div class="chat_people">
                      <div class="chat_img"> <img src="https://ptetutorials.com/images/user-profile.png" alt="sunil"> </div>
                      <div class="chat_ib">
                        <h5 class='name'>${nome}</h5>
                        <p class='msg-display new_msg_preview'>${mensagem}</p>
                      </div>
                    </div>
                  </div>`)
    }
  }
}


function is_contato_active(nome){
    let div_contato_active = $(`h5.name:contains('${nome}')`).closest('div.chat_list').hasClass('active_chat')
    return div_contato_active
}

function update_msg_preview(nome, mensagem){
  let msg_preview = $(`h5.name:contains('${nome}')`).find('p.msg')
  msg_preview.html(`${mensagem}`)
  msg_preview.addClass('new_msg_preview')
}

socket.on('dados_contatos', function(data){
    debugando(data)
    $('.chat_list').bind("click", function(){
        console.log('Cliquei no elemento boladão!')
        $(this).addClass('active_chat');
        $(this).siblings('.chat_list').removeClass('active_chat');
        $('.msg_history').html('')
        let nome_contato = $(this).find('.name')[0].innerText
        let msg_preview = $(this).find('p.msg')
        if(msg_preview.hasClass('new_msg_preview')){
          msg_preview.removeClass('new_msg_preview')
        }
        socket.emit('contato_historico',{'contato':nome_contato})
    })
})

socket.on('historico_conversa', function(data){
    for(obj of data['dados']){
        let recebida = obj['recebida']
        let mensagem = obj['mensagem']
        let horario = obj['hora_mensagem']
        // console.log(recebida)
        if(recebida == true){
            $('.msg_history').append(
            `
            <div class="incoming_msg">
              <div class="incoming_msg_img"> <img src="https://ptetutorials.com/images/user-profile.png" alt="sunil"> </div>
                <div class="received_msg">
                  <div class="received_withd_msg">
                    <p>${mensagem}</p>
                    <span class="time_date">${horario}</span></div>
                </div>
              </div>`)

        }
        else if(recebida == false){
            $('.msg_history').append(`
            <div class="outgoing_msg">
              <div class="sent_msg">
                <p>${mensagem}</p>
                <span class="time_date">${horario}</span></div>
            </div>`)
        }
        
    }
})

socket.on('nova_msg', function(data){
  // console.log(data)
    add_contato(data)
    for(obj of data['dados']){
        let nome = obj['contato']
        let mensagem = obj['mensagem']
        let hora_msg = obj['hora_mensagem']
        let verifica_contato = is_contato_active(nome)
        if(verifica_contato == true){
          $('.msg_history').append(
            `
            <div class="incoming_msg">
              <div class="incoming_msg_img"> <img src="https://ptetutorials.com/images/user-profile.png" alt="sunil"> </div>
                <div class="received_msg">
                  <div class="received_withd_msg">
                    <p>${mensagem}</p>
                    <span class="time_date">${horario}</span></div>
                </div>
              </div>`)
            document.querySelector('.msg_history').scrollTop = document.querySelector('.messages').scrollHeight;
        }
        else{
            update_msg_preview(nome, mensagem)
        }
    }

})