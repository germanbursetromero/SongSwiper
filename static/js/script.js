document.addEventListener('DOMContentLoaded', () => {
    const likeButton = document.getElementById('like-button');
    const dislikeButton = document.getElementById('dislike-button');

    likeButton.addEventListener('click', () => handleAction('like'));
    dislikeButton.addEventListener('click', () => handleAction('dislike'));

    async function handleAction(action) {
        const response = await fetch('/swipeAction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: action }),
        });

        const data = await response.json();
        updateSong(data);
    }

    function updateSong(song) {
        document.getElementById('song-title').textContent = song.name;
        document.getElementById('song-artist').textContent = song.artists[0].name;
        document.getElementById('song-preview').src = song.preview_url;
    }
});
