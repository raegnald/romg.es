<script lang="ts">
    import Spinner from "../components/Spinner.svelte";
    import FourOFour from "./FourOFour.svelte";

    export let meta: any = null;
    $: slug = meta?.params?.slug;

    let info: any;

    const articles = import.meta.glob("../articles/*.svelte");

    let ArticleContent: any;
    let loaded: boolean = false;

    $: if (slug) {
        const loader = articles[`../articles/${slug}.svelte`];
        if (loader) {
            loader()
                .then((module: any) => {
                    ArticleContent = module.default;
                    info = module.meta;
                })
                .finally(() => (loaded = true));
        } else {
            loaded = true;
        }
    }

    $: if (loaded) {
        if (info.title != undefined && info.title != "") {
            document.title = info.title;
        } else if (info.text != undefined && info.text != "") {
            document.title = info.text;
        } else {
            document.title = "Article on romg.es";
        }
    }
</script>

{#if ArticleContent}
    <svelte:component this={ArticleContent} />
{:else if loaded}
    <FourOFour />
{:else}
    <center><Spinner /></center>
    <p class="center emph">Loading...</p>
{/if}
