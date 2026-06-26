chrome.tabs.query(

    {

        active:true,

        currentWindow:true

    },

    function(tabs){

        let currentURL=tabs[0].url;

        document.getElementById("domain").innerText=currentURL;

        fetch("http://127.0.0.1:5000/check",{

            method:"POST",

            headers:{

                "Content-Type":"application/json"

            },

            body:JSON.stringify({

                url:currentURL

            })

        })

        .then(r=>r.json())

        .then(data=>{

            const verdict=data.verdict;

            const score=Math.round(data.final_score*100);

            const confidence=Math.round(

                data.deep_learning.confidence*100

            );

            document.getElementById("score").innerText=score+"%";

            document.getElementById("confidence").innerText=confidence+"%";

            document.getElementById("reason").innerText=

                data.reasons[0] ||

                "No suspicious indicators.";

            const verdictBox=document.getElementById("verdict");

            verdictBox.innerText=verdict;

            verdictBox.className="";

            if(verdict==="SAFE"){

                verdictBox.classList.add("safe");

            }

            else if(verdict==="SUSPICIOUS"){

                verdictBox.classList.add("suspicious");

            }

            else{

                verdictBox.classList.add("phishing");

            }

        })

        .catch(()=>{

            document.getElementById("verdict").innerText="Backend Offline";

        });

    }

);

// Open URLShieldNet Dashboard
document.getElementById("details").addEventListener("click", function () {

    chrome.tabs.create({

        url: "http://127.0.0.1:5500/frontend/login.html"

    });

});