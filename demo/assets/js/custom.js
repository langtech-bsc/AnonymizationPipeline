//navbar logo and source icons (docker, github) html
const navBarTitleHtml = `<div class="css-14xtw13 e8zbici0" style="
            right: unset !important;
        "><span kind="header" class="css-9s5bis edgvbvh3 demo-title" style="
            font-size: 18px; color: white;
        ">Anonimizador
        </span></div>`

 const sourceLinks = `<span class="css-9s5bis" aria-haspopup="true" aria-expanded="false"><a title="Github" target="_blank" href="https://github.com/TeMU-BSC/AnonymizationPipeline">
    <i style="color: #fff;" class="fa-brands fa-github fa-xl"></i>
</a></span><span class="css-9s5bis" aria-haspopup="true" aria-expanded="false"><a title="Docker Hub" target="_blank" href="https://hub.docker.com/r/bsctemu/anonymization-pipeline">
    <i style="color: #fff;" class="fa-brands fa-docker fa-xl"></i>
</a></span>`

//footer custom images html
const footerHtml = `<div class="footer-custom-images"">      
                    <a target="_blank" title="Barcelona Supercomputing Center" href="https://www.bsc.es"><img alt="BSC logo" src="/assets/custom-images/BSC-blue-small.png"></a>
                    <a target="_blank" title="Plan de Impulso de las Tecnologías del Lenguaje" href="https://plantl.mineco.gob.es/Paginas/index.aspx"><img alt="Plan TL logo" src="./assets/custom-images/plantl.png"></a>
                    <a target="_blank" title="Ministerio de Asuntos Económicos y Transformación Digital" href="https://portal.mineco.gob.es/en-us/Pages/index.aspx"><img alt="Mineco logo" src="./assets/custom-images/gob-es.png"></a>
                    <a target="_blank" title="Digitalisation and Artificial Intelligence - Telecommunications and Digital Infrastructure" href="https://avancedigital.mineco.gob.es/en-us/Paginas/index.aspx"><img alt="SEAD logo" src="/assets/custom-images/secretaria-es.png"></a>
            </div>`

window.parent.document.querySelector('header').insertAdjacentHTML('afterbegin', navBarTitleHtml);
window.parent.document.querySelector('div[data-testid="stToolbar"]').insertAdjacentHTML('afterbegin', sourceLinks);
window.parent.document.querySelector('footer').insertAdjacentHTML('afterbegin', footerHtml)