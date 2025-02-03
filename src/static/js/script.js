async function searchDocuments() {
    try {
        const query = document.getElementById('query').value;
        window.location.href = `/search?query=${encodeURIComponent(query)}`;
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

async function viewDocument(document_num) {
    try {
        window.open(`/view_document?document_num=${encodeURIComponent(document_num)}`, '_blank');
    } catch (error) {
        console.error('Ошибка:', error);
    }
}