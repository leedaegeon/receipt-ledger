package com.receiptledger

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.lifecycle.viewmodel.compose.viewModel
import com.receiptledger.ui.common.AppShell
import com.receiptledger.ui.common.DemoLedgerPipeline
import com.receiptledger.ui.common.LedgerViewModel
import com.receiptledger.ui.common.LedgerViewModelFactory
import com.receiptledger.ui.common.ProcessLedgerPipeline
import com.receiptledger.ui.theme.ReceiptLedgerTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            ReceiptLedgerTheme {
                Surface(color = MaterialTheme.colorScheme.background) {
                    val pipeline = if (BuildConfig.USE_DEMO_PIPELINE) {
                        DemoLedgerPipeline()
                    } else {
                        ProcessLedgerPipeline()
                    }
                    val vm: LedgerViewModel = viewModel(factory = LedgerViewModelFactory(pipeline))
                    AppShell(viewModel = vm)
                }
            }
        }
    }
}
