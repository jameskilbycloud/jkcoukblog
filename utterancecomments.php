<?php
/**
 * Utterances-only comments template.
 *
 * @package Infinity Blog
 */

if (post_password_required()) {
    return;
}
?>

<div id="comments" class="comments-area">
    <div class="pb-30">
        <!-- Utterances Comments Embed -->
        <section id="utterances-comments">
            <script src="https://utteranc.es/client.js"
                repo="jameskilbynet/wordpresscomments"
                issue-term="pathname"
                theme="github-light"
                crossorigin="anonymous"
                async>
            </script>
        </section>
    </div>
</div><!-- #comments -->
