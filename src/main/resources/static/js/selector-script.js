function moveItem(checkbox) {
    const itemContainer = checkbox.closest('.file-item-transition');
    const targetContainer = checkbox.checked ?
        document.getElementById('selectedContainer') :
        document.getElementById('unselectedContainer');

    // 애니메이션 클래스 추가
    itemContainer.classList.add('item-moving');

    // 약간의 지연 후 이동 실행
    setTimeout(() => {
        targetContainer.appendChild(itemContainer);
        itemContainer.classList.remove('item-moving');
    }, 300);
}

async function processSelectedFiles() {
    const button = document.getElementById('processButton');
    const spinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');

    const selectedFiles = Array.from(document.getElementById('selectedContainer')
        .querySelectorAll('input[name="cogsFiles"]'))
        .map(checkbox => checkbox.value);

    if (selectedFiles.length === 0) {
        showError('Please select at least one module');
        return;
    }

    try {
        button.disabled = true;
        spinner.classList.remove('hidden');
        errorMessage.classList.add('hidden');

        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ selectedFiles })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to process files');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'BotLauncher.zip';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        // 다운로드 후 선택 해제 및 아이템 이동
        uncheckAllItems();
    } catch (error) {
        showError(error.message);
    } finally {
        button.disabled = false;
        spinner.classList.add('hidden');
    }
}

function uncheckAllItems() {
    const selectedContainer = document.getElementById('selectedContainer');
    const unselectedContainer = document.getElementById('unselectedContainer');
    const selectedItems = Array.from(selectedContainer.querySelectorAll('.file-item-transition'));

    selectedItems.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        checkbox.checked = false;
        item.classList.add('item-moving');

        setTimeout(() => {
            unselectedContainer.appendChild(item);
            item.classList.remove('item-moving');
        }, 300);
    });
}

function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
    setTimeout(() => {
        errorElement.classList.add('hidden');
    }, 5000);
}