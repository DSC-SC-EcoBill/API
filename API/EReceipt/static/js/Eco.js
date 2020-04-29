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
            var httpRequest;
            httpRequest = new XMLHttpRequest();
            httpRequest.onreadystatechange = function(){
                if(httpRequest.status === 200){

                }else{
                    alert(httpRequest.status);
                }
            };
            httpRequest.open('POST', 'http://127.0.0.1:8000/api/pos/chargepost/', true);

            var aJson = new Object();

            aJson.total_amount = "4000";
            aJson.items = "a";
            aJson.prices = "3";

            httpRequest.send(JSON.stringify(aJson));
        }

