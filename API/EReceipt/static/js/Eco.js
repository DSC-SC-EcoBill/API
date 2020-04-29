        var total = 0;
        var product_list = new Array();
        var product_price = new Array();
        var x = 0;
        var pc = 0;
        var pr = 0;
        var br = "\n";

        function but(su){
            total += parseInt(su);
            document.getElementById('disp').value = total;

            var e = window.event,
            btn = e.target || e.srcElement;
            var pro = document.getElementById('Pro');
            pc=btn.id+br;
            pro.value += pc;
            var price = document.getElementById('price');
            pr=su+br;
            price.value += pr;
            product_list[x]=btn.id;
            product_price[x]=su;
            x++;
        }

        function c(){
        flag = true;
        total= 0;
        document.getElementById('disp').value = "0";
        document.getElementById('Pro').value = "";
        document.getElementById('price').value = "";
        product_list = [];
        product_price = [];
        x = 0;
        }

        // 서버에 데이터 보내는 함수
        function send() {
        var aJson = new Object();
        aJson.total_amount = total;
        aJson.items = product_list;
        aJson.prices = product_price;

        var httpRequest = new XMLHttpRequest();

        httpRequest.onreadystatechange = function(){
            if(httpRequest.readyState === XMLHttpRequest.DONE){
                alert('준비끝');
            }
            else{
                alert('준비 안 끝');
            }

            if(httpRequest.status === 200) {
                alert(httpRequest.responseText);
                document.getElementById('img').src=httpRequest.responseText;
            }else{
                alert("이상있음!");
            }
        }
        httpRequest.open('POST', '/api/pos/chargepost/', false);
        httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
        httpRequest.send(JSON.stringify(aJson));
    }