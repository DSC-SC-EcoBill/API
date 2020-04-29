        var total = 0;
        var product_list = [];
        var product_price = [];
        var x,pc,pr = 0;
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
        var httpRequest = new XMLHttpRequest();
        var aJson = new Object();

        httpRequest.open('POST', '/api/pos/chargepost/');
        httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');

        aJson.total_amount = "4000";
        aJson.items = "a";
        aJson.prices = "3";

        JSON.stringify(aJson);
        httpRequest.send(JSON.stringify(aJson));
    }